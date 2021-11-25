import os
import json
from pkg_resources import resource_filename, resource_string

import click

from ocrd import Processor
from ocrd_modelfactory import page_from_file
from ocrd_utils import (
    getLogger,
    make_file_id,
    assert_file_grp_cardinality,
    MIMETYPE_PAGE,
    coordinates_for_segment,
    points_from_polygon,
    polygon_from_points
)
from ocrd_models.ocrd_page import (
    CoordsType,
    TextRegionType,
    GraphicRegionType,
    TableRegionType,
    ImageRegionType,
    to_xml,
    RegionRefIndexedType, OrderedGroupType, ReadingOrderType
)

from origami.core.page import Page, Annotations
from origami.core.predict import PredictorType
from origami.core.segment import Segmentation, SegmentationPredictor
from origami.core.dewarp import Dewarper
from origami.batch.detect.contours import ContoursProcessor
from origami.batch.core.processor import Processor as BatchProcessor

OCRD_TOOL = json.loads(resource_string(__name__, 'ocrd-tool.json').decode('utf8'))
TOOL = 'ocrd-origami-segment'

# FIXME: wrap separately (via parameters):
# - region post-processing
# - baseline detection
# - baseline polygonalization
# - (re-)ordering by RXYC

# use Origami's CLI default options here
@click.command()
@BatchProcessor.options
@ContoursProcessor.options
def contourer(**kwargs):
    # prevent sys.argv interference:
    kwargs['args'] = {}
    kwargs['standalone_mode'] = False
    # override defaults:
    # args={region_area=0.0025, separator_threshold=0.004, margin_distance=0.01, margin_width=0.05}
    # kwargs.update(args)
    return ContoursFunctor(kwargs)

# instead of Origami's (zip-)file-based annotation batch processing,
# recreate the main functionality from origami.batch.detect.contours
# by in-memory aggregation of results here:
class ContoursFunctor(ContoursProcessor):
    def __init__(self, options):
        print(f"ContoursFunctor options: {options}")
        super(ContoursFunctor, self).__init__(options)

    def __call__(self, annotations):
        handlers = dict((
            (PredictorType.REGION, self._process_region_contours),
            (PredictorType.SEPARATOR, self._process_separator_contours)
        ))
        result = DictWriter()
        predictions = []
        for prediction in annotations.segmentation.predictions:
            handlers[prediction.type](result, annotations, prediction)
            predictions.append(dict(name=prediction.name,
                                    type=prediction.type.name))
        result['predictions'] = predictions
        return result

# replacement for zipfile
class DictWriter(dict):
    def writestr(self, path, value):
        self[path] = value

# instead of Origami's (image file) path-based data passing,
# recreate the functionality of origami.core.page by PIL.Image here:
class PillowPage(Page):
    def __init__(self, image, dewarping_transform=None):
        self._warped = image # .convert('L')

        # verbatim from origami.core.page.Page:
        if dewarping_transform is not None:
            self._dewarper = Dewarper(self._warped, dewarping_transform)
            self._dewarped = self._dewarper.dewarped
        else:
            self._dewarper = None
            self._dewarped = None

class ModularSegmentationPredictor(SegmentationPredictor):
    def __init__(self, *args, **kwargs):
        types = kwargs.pop('types', None)
        super(ModularSegmentationPredictor, self).__init__(*args, **kwargs)
        if types:
            # unload Region/blkx or Separator/sep or both
            self._predictors = [predictor for predictor in self._predictors
                                if predictor.type in types]
    # instead of Page/filepath:
    def __call__(self, image):
        page = PillowPage(image)
        segmentation = Segmentation([p(page) for p in self._predictors])
        return Annotations(page, segmentation)

class OcrdOrigamiSegment(Processor):

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = OCRD_TOOL['tools'][TOOL]
        kwargs['version'] = OCRD_TOOL['version']
        super(OcrdOrigamiSegment, self).__init__(*args, **kwargs)
        if hasattr(self, 'output_file_grp'):
            # processing context
            self.setup()

    def setup(self):
        """Set up the model prior to processing."""
        types = []
        if self.parameter['detect-seps']:
            types.append(PredictorType.SEPARATOR)
        if self.parameter['detect-blks']:
            types.append(PredictorType.REGION)
        self.predictor = ModularSegmentationPredictor(
            # resolve relative path via OCR-D ResourceManager
            self.resolve_resource(self.parameter['model']),
            grayscale=self.parameter['grayscale'],
            target=self.parameter['target'],
            types=types)
        self.contourer = contourer()

    def process(self):
        """Perform segmentation using Origami on the workspace.

        Load model types given by ``detect-blks`` (i.e. regions)
        and ``detect-seps`` (i.e. separators).
        ...
        """
        assert_file_grp_cardinality(self.input_file_grp, 1)
        assert_file_grp_cardinality(self.output_file_grp, 1)

        LOG = getLogger('OcrdOrigamiSegment')
        #oplevel = self.parameter['operation_level']
        for input_file in self.input_files:
            pcgts = page_from_file(self.workspace.download_file(input_file))
            self.add_metadata(pcgts)
            page = pcgts.get_Page()
            page_id = input_file.pageId or input_file.ID
            LOG.info('Processing page "%s"', page_id)

            page_image, page_coords, page_image_info = self.workspace.image_from_page(
                page, page_id, feature_filter='binarized')

            annotation = self.predictor(page_image)
            for prediction in annotation.segmentation.predictions:
                LOG.debug("Detected %d segments of type %s (with %d classes)",
                          prediction.labels.max(), prediction.type, len(prediction.classes))
            result = self.contourer(annotation)
            print(result)
            exit() # FIXME: parse shapely wkt strings, annotate into PAGE

            file_id = make_file_id(input_file, self.output_file_grp)
            pcgts.set_pcGtsId(file_id)
            self.workspace.add_file(
                ID=file_id,
                file_grp=self.output_file_grp,
                pageId=input_file.pageId,
                mimetype=MIMETYPE_PAGE,
                local_filename=os.path.join(self.output_file_grp, file_id + '.xml'),
                content=to_xml(pcgts).encode('utf-8')
            )
