package org.traccar.helper;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.traccar.model.Position;


public class KalmanFilter {
    private static final Logger LOGGER = LoggerFactory.getLogger(KalmanFilter.class);

    private long timeStamp; // In millisecond
    private double latitude; // In degrees
    private double longitude; // In degrees
    private float variance; // P matrix. Initial estimate of error
    public static final float MIN_ACCURACY = 100f; // Increase/decrease based on usage

    public KalmanFilter() {
        variance = -1;
    }

    // Set previous state
    public void setState(double latitude, double longitude, long timeStamp, float accuracy) {
        this.latitude = latitude;
        this.longitude = longitude;
        this.timeStamp = timeStamp;
        this.variance = accuracy * accuracy;
    }

    /**
     * Kalman filter processing for latitude and longitude
     * <p>
     * newLatitude - new measurement of latitude
     * newLongitude - new measurement of longitude
     * accuracy - measurement of 1 standard deviation error in meters
     * newTimeStamp - time of measurement in millis
     */
    public Position applyFilter(Position position) {
        LOGGER.info("Before > " +position.getLatitude() + "," + position.getLongitude());
        if (variance < 0) {
            // if variance < 0, object is uninitialised, so initialise with current values
            setState(position.getLatitude(), position.getLongitude(), position.getFixTime().getTime(), MIN_ACCURACY);
        } else {
            // else apply Kalman filter
            long duration = position.getFixTime().getTime() - this.timeStamp;
            if (duration > 0) {
                // time has moved on, so the uncertainty in the current position increases
                variance += duration * position.getSpeed() * position.getSpeed() / 1000;
                timeStamp = position.getFixTime().getTime();
            }

            // Kalman gain matrix 'k' = Covariance * Inverse(Covariance + MeasurementVariance)
            // because 'k' is dimensionless,
            // it doesn't matter that variance has different units to latitude and longitude
            float k = variance / (variance + MIN_ACCURACY * MIN_ACCURACY);
            // apply 'k'
            latitude += k * (position.getLatitude() - latitude);
            longitude += k * (position.getLongitude() - longitude);
            // new Covariance matrix is (IdentityMatrix - k) * Covariance
            variance = (1 - k) * variance;

            // Return filtered point
            position.setLongitude(longitude);
            position.setLatitude(latitude);
            LOGGER.info("After > " +position.getLatitude() + "," + position.getLongitude());
        }
        return position;
    }
}
