poetry run celery worker \
    --app=celery_issues.celery \
    -l info --prefetch-multiplier=1 \
    --concurrency=1 --pool=prefork --without-gossip
