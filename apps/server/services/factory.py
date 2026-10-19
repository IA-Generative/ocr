import boto3
from services.base.pipeline import Pipeline
from business.cache.sql_cache import TaskCache

# Models
from business.checkbox_service.models.morpho import MorphoBoxDetection
from business.paddleocr2.models.paddle import PaddleInferOCR2

# Workers
from business.forms.workers.pdf_worker import (
    PDFFormsExtractorWorker,
    DefaultPdfExtractor,
)

from services.base.worker import AnyFileProcessWorker, DefaultFileProcessWorker

from business.paddleocr2.configs.paddle import PaddleSetting
from src.config.ocr_model import OCRModelSettings

from src.connector import S3Connector, s3_settings

s3_client = boto3.client("s3", verify=s3_settings.VERIFY_SSL)
s3_client_connector = S3Connector(s3_client=s3_client, bucket_name=s3_settings.AWS_BUCKET_NAME)
main_ocr_settings = OCRModelSettings()


LAYOUT_PROCESS_NAME = "layout"
TABLE_PROCESS_NAME = "table"


def load_layout_worker(worker_weight: float = 1) -> Pipeline:
    """Worker de détection des zones (queue ``layout``), exécuté en parallèle de l'OCR."""
    from business.layout.configs.layout import LayoutSettings
    from business.layout.models.layout_detection import LayoutDetectionModel
    from business.layout.worker.layout_worker import LayoutWorker

    settings = LayoutSettings()
    return Pipeline(
        workers=[
            LayoutWorker(
                name="layout-worker",
                file_connector=s3_client_connector,
                models=[LayoutDetectionModel(settings=settings)],
                batch_size=settings.LAYOUT_BATCH_SIZE,
                worker_weight=worker_weight,
                settings=settings,
            )
        ]
    )


def load_table_worker(worker_weight: float = 1) -> Pipeline:
    """Worker de structure des tables (queue ``table``), alimenté par le worker layout."""
    from business.layout.configs.layout import LayoutSettings
    from business.layout.models.table_structure import TableStructureModel
    from business.layout.worker.table_worker import TableWorker

    settings = LayoutSettings()
    return Pipeline(
        workers=[
            TableWorker(
                name="table-worker",
                file_connector=s3_client_connector,
                models=[TableStructureModel(settings=settings)],
                batch_size=1,
                worker_weight=worker_weight,
                settings=settings,
            )
        ]
    )


def load_worker(
    name: str,
    batch_size: int = 1,
    worker_weight: float = 1,
) -> Pipeline:
    if name == LAYOUT_PROCESS_NAME:
        return load_layout_worker(worker_weight=worker_weight)
    if name == TABLE_PROCESS_NAME:
        return load_table_worker(worker_weight=worker_weight)

    # logger.info(f"---- {name} selected ----")
    ################# CACHE CLIENT ##################
    cache = TaskCache(file_connector=s3_client_connector)
    #################################################

    #################    MODELS   ####################
    ocr_model = PaddleInferOCR2(PaddleSetting().PADDLE_OCR_BASE_DIR)
    morpho_model = MorphoBoxDetection()
    ##################################################

    ################# WORKERS ########################
    default_worker = DefaultFileProcessWorker(
        name="default-worker",
        file_connector=s3_client_connector,
        models=[ocr_model, morpho_model],
        batch_size=2,
        worker_weight=worker_weight,
        cache=cache,
    )
    # Si c'est un pdf and un vrai formulaire (donnée issue de is_form_pdf) on rentre dans ce worker
    # extraction native des champs de formulaire PDF (widgets AcroForm), sans LLM
    worker_pdf = PDFFormsExtractorWorker(
        name="pdf-form-widget-extractor",
        file_connector=s3_client_connector,
        models=[],
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )
    default_worker_pdf = DefaultPdfExtractor(
        name="default-pdf-worker",
        file_connector=s3_client_connector,
        models=[],
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )

    # On rentre dedans dans les autre cas
    any_file_worker = AnyFileProcessWorker(
        name="any-file-worker",
        file_connector=s3_client_connector,
        models=[
            ocr_model,
            morpho_model,
        ],
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )

    ##################################################
    ################# FILE WORKERS ###################
    try:
        from business.liteparse.models.liteparse_model import LiteparseExtractionModel
        from business.liteparse.worker.liteparse_worker import LiteparseWorker

        liteparse_worker = LiteparseWorker(
            name="liteparse-worker",
            file_connector=s3_client_connector,
            models=[LiteparseExtractionModel(file_connector=s3_client_connector)],
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )
        _office_image_workers = [liteparse_worker]  # TaskOperation.DEFAULT — office + image files
    except ImportError as e:
        print(f"liteparse not available, falling back to individual file workers: {e}")
        from business.extractions.worker.file_worker import (
            CSVWorker,
            DocxWorker,
            XlsxWorker,
            OdtWorker,
            OdsWorker,
            OdpWorker,
        )

        _office_image_workers = [
            CSVWorker(
                name="csv-worker",
                file_connector=s3_client_connector,
                batch_size=batch_size,
                worker_weight=worker_weight,
                cache=cache,
            ),
            XlsxWorker(
                name="xlsx-worker",
                file_connector=s3_client_connector,
                batch_size=batch_size,
                worker_weight=worker_weight,
                cache=cache,
            ),
            DocxWorker(
                name="docx-worker",
                file_connector=s3_client_connector,
                batch_size=batch_size,
                worker_weight=worker_weight,
                cache=cache,
            ),
            OdtWorker(
                name="odt-worker",
                file_connector=s3_client_connector,
                batch_size=batch_size,
                worker_weight=worker_weight,
                cache=cache,
            ),
            OdsWorker(
                name="ods-worker",
                file_connector=s3_client_connector,
                batch_size=batch_size,
                worker_weight=worker_weight,
                cache=cache,
            ),
            OdpWorker(
                name="odp-worker",
                file_connector=s3_client_connector,
                batch_size=batch_size,
                worker_weight=worker_weight,
                cache=cache,
            ),
        ]
    ##################################################
    ##################################################
    workers = [
        *_office_image_workers,  # TaskOperation.DEFAULT — office + image files (liteparse ou fallback)
        default_worker_pdf,  # TaskOperation.DEFAULT and application/pdf AND is_form_pdf
        default_worker,  # TaskOperation.DEFAULT
        worker_pdf,  # application/pdf AND is_form_pdf
        any_file_worker,  # OTHER
    ]

    try:
        from business.docling_inference.worker.docling_worker import DoclingWorker
        from business.docling_inference.models.inference import DoclingInferenceModel

        model_docling = DoclingInferenceModel()
        worker_docling = DoclingWorker(
            name="docling-worker",
            file_connector=s3_client_connector,
            models=[model_docling],
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )
        workers.insert(3, worker_docling)  # TaskOperation.DOCLING

    except ImportError as e:
        print(e)

    return Pipeline(workers=workers)
