FROM frappe/frappe-worker:v15

USER frappe

# Pre-fetch apps to make container startup faster
RUN bench get-app ury https://github.com/889Anonymous/vu_caffe --branch main
# vu_caffe_custom is local, so we just copy it during development or mount it
