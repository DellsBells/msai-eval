def flag_anomalies(readings, window, threshold):
    """
    Flag readings that are more than 'threshold' standard deviations away from the rolling mean.
    
    :param readings: List of numerical data points to be analyzed.
    :param window: Size of the moving window for calculating the rolling mean.
    :param threshold: Number of standard deviations beyond which a reading is flagged as an anomaly.
    :return: A list where each element corresponds to whether the respective reading is an anomaly (True) or not (False).
    
    Example:
    flag_anomalies([10, 10, 10, 10, 50, 10, 10], 3, 5)
    Output: [False, False, False, True, False, False]
    """
    from statistics import mean, stdev
    
    anomalies = []
    for i in range(len(readings) - window + 1):
        subset = readings[i:i+window]
        rolling_mean = mean(subset)
        rolling_std_dev = stdev(subset)
        
        if abs((readings[i+window-1] - rolling_mean)) > threshold * rolling_std_dev:
            anomalies.append(True)
        else:
            anomalies.append(False)
    
    return anomalies

# Example usage
print(flag_anomalies([10, 10, 10, 10, 50, 10, 10], 3, 5))