import datetime

from flask import render_template

from . import app_routes
from src.services.netlify.analytics import get_analytics_data


@app_routes.route("/analytics")
def analytics():
    """
    Renders the main analytics page.
    """
    analytics_data = get_analytics_data()

    # Helper to format bytes to human-readable format
    def format_bytes(bytes_val):
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.2f} KB"
        elif bytes_val < 1024 * 1024 * 1024:
            return f"{bytes_val / (1024 * 1024):.2f} MB"
        else:
            return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"

    # Helper to process time-series data for Chart.js
    def process_chart_data(metric_key):
        labels = []
        data_points = []
        if (
            metric_key in analytics_data
            and "data" in analytics_data[metric_key]
            and not analytics_data[metric_key].get("error")
        ):
            # Data is in format [[timestamp, count], ...]
            for entry in analytics_data[metric_key]["data"]:
                if len(entry) > 1:
                    timestamp_ms = entry[0]
                    count = entry[1]
                    # Convert timestamp (milliseconds) to datetime object
                    dt_object = datetime.datetime.fromtimestamp(timestamp_ms / 1000)
                    labels.append(
                        dt_object.strftime("%Y-%m-%d")
                    )  # Format date as YYYY-MM-DD
                    data_points.append(count)
        return labels, data_points

    # --- Process and prepare data for template ---
    total_pageviews = 0
    pageview_labels, pageview_data = process_chart_data("pageviews")
    total_pageviews = sum(pageview_data)  # Sum up the data points for total

    total_visitors = 0
    visitor_labels, visitor_data = process_chart_data("visitors")
    total_visitors = sum(visitor_data)  # Sum up the data points for total

    total_bandwidth = 0
    if (
        "bandwidth" in analytics_data
        and "data" in analytics_data["bandwidth"]
        and not analytics_data["bandwidth"].get("error")
    ):
        for entry in analytics_data["bandwidth"]["data"]:
            total_bandwidth += entry.get("siteBandwidth", 0)
    formatted_total_bandwidth = (
        format_bytes(total_bandwidth) if total_bandwidth > 0 else "0 B"
    )

    top_countries = []
    if (
        "ranking/countries" in analytics_data
        and "data" in analytics_data["ranking/countries"]
        and analytics_data["ranking/countries"]["data"]
        and not analytics_data["ranking/countries"].get("error")
    ):
        top_countries = analytics_data["ranking/countries"]["data"]

    return render_template(
        "analytics.html",
        total_pageviews=total_pageviews,
        total_visitors=total_visitors,
        total_bandwidth=formatted_total_bandwidth,
        top_countries=top_countries,
        pageview_labels=pageview_labels,
        pageview_data=pageview_data,
        visitor_labels=visitor_labels,
        visitor_data=visitor_data,
        raw_data=analytics_data,
    )
