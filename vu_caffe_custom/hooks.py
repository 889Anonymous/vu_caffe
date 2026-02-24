app_name = "vu_caffe_custom"
app_title = "Vu Caffe Custom"
app_publisher = "Nguyễn Trường"
app_description = "Tối ưu POS mini cho quán cà phê Vu Caffe"
app_icon = "octicon octicon-coffee"
app_color = "green"
app_email = "your@email.com"
app_license = "MIT"

# Scheduled Tasks
scheduler_events = {
    "cron":{
        "0 8 * * *": [
            "vu_caffe_custom.vu_caffe_custom.scripts.scheduler_vu_caffe.update_daily_report"
        ]
    }
}
