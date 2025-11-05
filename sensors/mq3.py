from core.hardware_manager import hardware_manager
import random
import time

# Since Raspberry Pi doesn't have a built-in ADC, we'll use spidev for a 
# common ADC like the MCP3008. If spidev isn't installed, it will only work in simulation.
try:
    import spidev
except ImportError:
    spidev = None

class MQ3:
    def __init__(self, channel=0):
        self.channel = channel
        self.simulation_mode = hardware_manager.simulation_mode
        self.spi = None
        
        if not self.simulation_mode:
            if spidev is None:
                print("Warning: spidev library not found. MQ3 sensor will run in simulation mode.")
                self.simulation_mode = True
            else:
                self.spi = spidev.SpiDev()
                self.spi.open(0, 0)  # Open SPI bus 0, device 0
                self.spi.max_speed_hz = 1350000
                print(f"MQ-3 Alcohol Sensor initialized on ADC channel {self.channel}")

    def read_alcohol_level(self):
        """
        Reads the raw analog value and returns it.
        A real implementation would convert this value to mg/L based on calibration.
        """
        if self.simulation_mode:
            # print("Reading alcohol level (simulated)...")
            return random.uniform(0.05, 0.4)

        # Read SPI data from the MCP3008
        adc = self.spi.xfer2([1, (8 + self.channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data

    def calibrate(self):
        """
        Simulates a calibration period for the sensor to warm up.
        """
        print("Calibrating MQ-3 sensor (warming up)... Please wait 20 seconds.")
        if not self.simulation_mode:
            # In a real scenario, you'd wait for the sensor reading to stabilize.
            time.sleep(20)
        print("Calibration complete.")

    def close(self):
        if not self.simulation_mode and self.spi is not None:
            try:
                self.spi.close()
                print("MQ-3 sensor SPI connection closed.")
            except Exception as exc:
                print(f"Warning: Failed to close MQ-3 SPI connection: {exc}")
            finally:
                self.spi = None

if __name__ == '__main__':
    # Example usage
    mq3_sensor = MQ3(channel=0)
    mq3_sensor.calibrate()
    try:
        while True:
            alcohol_value = mq3_sensor.read_alcohol_level()
            if mq3_sensor.simulation_mode:
                print(f"Simulated alcohol level: {alcohol_value:.2f} (raw value)")
            else:
                print(f"Raw ADC value: {alcohol_value}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if not mq3_sensor.simulation_mode and mq3_sensor.spi:
            mq3_sensor.spi.close()
            print("SPI connection closed.")
