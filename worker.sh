poetry run celery \
    --app=celery_issues.celery worker \
    -l info --prefetch-multiplier=1 \
    --concurrency=1 --pool=prefork --without-gossip
