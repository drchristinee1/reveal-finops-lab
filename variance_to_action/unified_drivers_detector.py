def aggregate_results(self) -> dict:
    """
    Aggregate normalized driver detection results into a unified summary.
    """
    all_normalized_results = []

    # Collect all normalized results from each detector
    for detector_result in self.results.values():
        if not detector_result:
            continue

        if isinstance(detector_result, list):
            all_normalized_results.extend(detector_result)
        elif isinstance(detector_result, dict):
            # Common patterns: {"results": [...]} or a single dict result
            if "results" in detector_result and isinstance(detector_result["results"], list):
                all_normalized_results.extend(detector_result["results"])
            else:
                all_normalized_results.append(detector_result)

    # Group by driver
    driver_groups = {}

    for item in all_normalized_results:
        driver = item.get("driver", "unknown")

        if driver not in driver_groups:
            driver_groups[driver] = {
                "total_cost": 0,
                "resources": [],
                "services": set()
            }

        driver_groups[driver]["total_cost"] += item.get("estimated_monthly_cost", 0)

        resource = item.get("resource", "unknown_resource")
        driver_groups[driver]["resources"].append(resource)

        service = item.get("service", "unknown")
        driver_groups[driver]["services"].add(service)

    # Convert services set to list for JSON serialization
    for driver in driver_groups:
        driver_groups[driver]["services"] = list(driver_groups[driver]["services"])

    # Sort drivers by cost descending
    top_drivers = sorted(
        driver_groups.items(),
        key=lambda x: x[1]["total_cost"],
        reverse=True
    )

    return {
        "summary": {
            "total_drivers": len(driver_groups),
            "total_results": len(all_normalized_results),
            "total_estimated_monthly_cost": sum(
                group["total_cost"] for group in driver_groups.values()
            )
        },
        "drivers_by_cost": [
            {
                "driver": driver,
                "total_cost": details["total_cost"],
                "resource_count": len(details["resources"]),
                "resources": details["resources"],
                "services": details["services"]
            }
            for driver, details in top_drivers
        ]
    }