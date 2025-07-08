from config import celery_app
from model_ai.models import LlamaModel, DownloadStatus

from huggingface_hub import login
from huggingface_hub import hf_hub_download


def get_model(hf_token, name_model, name_file):
    login(token=hf_token)
    local_dir = 'model_ai/download'
    downloaded_file = hf_hub_download(repo_id=name_model, filename=name_file, local_dir=local_dir)


@celery_app.task()
def download_model(id):
    try:
        instance = LlamaModel.objects.get(id=id)
        get_model(instance.hf_token, instance.name_model, instance.name_file)
        instance.download_status = DownloadStatus.DOWNLOADED
    except:
        instance.download_status = DownloadStatus.ERROR
    instance.save()