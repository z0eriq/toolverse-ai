from __future__ import annotations

from celery import shared_task


@shared_task(name="apps.programmatic_seo.tasks.generate_programmatic_batch_task")
def generate_programmatic_batch_task(
    page_type: str = "use_case",
    limit: int = 10,
    locale: str = "en",
    publish: bool = False,
) -> dict:
    from apps.programmatic_seo.services import generate_programmatic_batch

    return generate_programmatic_batch(
        page_type=page_type,
        limit=limit,
        locale=locale,
        publish=publish,
    )
