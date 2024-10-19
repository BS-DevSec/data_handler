# plotter.py
import logging
from datetime import datetime, date
from typing import Optional, Any, Dict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

logger = logging.getLogger(__name__)

class Plotter:
    """Class to handle plotting of data."""

    def __init__(self, processor: Optional['DataProcessor'] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Plotter with a DataProcessor instance and configuration settings.

        :param processor: Instance of DataProcessor containing processed data.
        :param config: Dictionary containing plot configurations.
        """
        self.processor = processor
        plotter_config = config or {}
        self.figsize_main = plotter_config.get('figsize_main', [17, 12])
        self.figsize_kla = plotter_config.get('figsize_kla', [14, 8])
        self.style = plotter_config.get('style', 'darkgrid')
        self.plot_dir = Path(plotter_config.get('plot_dir', 'plot'))
        self.dpi = plotter_config.get('dpi', 300)

        # Ensure the plot directory exists
        self.plot_dir.mkdir(parents=True, exist_ok=True)

    def set_processor(self, processor: 'DataProcessor') -> None:
        """
        Set the DataProcessor instance.

        :param processor: Instance of DataProcessor containing processed data.
        """
        self.processor = processor

    def plot_data(self) -> None:
        """
        Plot the processed offline and online data and save the figure to the plot directory.
        """
        if self.processor is None:
            logger.error("DataProcessor is not set. Use set_processor() before plotting.")
            raise ValueError("DataProcessor is not set.")

        logger.info("Generating main culture simulation plots.")
        try:
            sns.set(style=self.style)

            fig, (ax1, ax2, ax3, ax4) = plt.subplots(
                4,
                gridspec_kw={'height_ratios': [1.5, 1.3, 1.3, 1.3]},
                figsize=self.figsize_main
            )

            label_font_size = 18
            tick_font_size = 14
            title_font_size = 20

            # Plot 1 - Glucose, Biomass, Ethanol
            ax1.set_xlim([0, 48])
            ax1.set_ylim([0, 25])
            ax1.set_ylabel(r"Glucose / g $\cdot$ L$^{-1}$", fontsize=label_font_size)
            ax1.tick_params(axis='x', labelsize=tick_font_size)
            ax1.tick_params(axis='y', labelsize=tick_font_size)

            ax1y2 = ax1.twinx()
            ax1y2.set_ylim([0, 75])
            ax1y2.set_ylabel(r"Ethanol, Biomass / g $\cdot$ L$^{-1}$", fontsize=label_font_size)
            ax1y2.tick_params(axis='y', labelsize=tick_font_size)
            time_feed_glucose_numeric = np.array(self.processor.time_feed_glucose_numeric)
            glucose_feed = np.array(self.processor.glucose_feed)
            valid_feed_glucose_mask = np.array(self.processor.valid_feed_glucose_mask)

            ax1.plot(
                self.processor.time_glucose,
                self.processor.glucose,
                color="#ff9933",
                marker="o",
                linestyle="--",
                linewidth=2,
                label="Glucose"
            )
            ax1y2.plot(
                self.processor.time_biomass,
                self.processor.biomass,
                color="#008b00",
                marker="^",
                linestyle="--",
                linewidth=2,
                label="Biomass"
            )
            ax1y2.plot(
                self.processor.time_ethanol,
                self.processor.ethanol,
                color="#3a5fcd",
                marker="s",
                linestyle="--",
                linewidth=2,
                label="Ethanol"
            )

            # Plot 2 - CO2, O2
            ax2.set_ylabel(r"CO$_2$ / %", fontsize=label_font_size)
            ax2y2 = ax2.twinx()
            ax2y2.set_ylabel(r"O$_2$ / %", fontsize=label_font_size)

            ax2.plot(
                self.processor.online_data['time'],
                self.processor.online_data['sCO2'],
                color="#31BF05",
                linestyle="-",
                linewidth=1,
                label="CO2"
            )
            ax2y2.plot(
                self.processor.online_data['time'],
                self.processor.online_data['sO2'],
                color="#36605A",
                linestyle="-",
                linewidth=1,
                label="O2"
            )

            # Plot 3 - pO2, Glucose Feed
            ax3.set_ylabel(r"spO$_2$ / %", fontsize=label_font_size)
            ax3y2 = ax3.twinx()
            ax3y2.set_ylabel(r"Glucose Feed / mL $\cdot$ min$^{-1}$", fontsize=label_font_size)

            ax3.plot(
                self.processor.online_data['time'],
                self.processor.online_data['spO2'],
                color="#27ABCF",
                linestyle="-",
                linewidth=1,
                label="spO2"
            )
            ax3y2.plot(
                time_feed_glucose_numeric[valid_feed_glucose_mask],
                glucose_feed[valid_feed_glucose_mask],
                color="#CD5B45",
                linestyle="-",
                linewidth=1,
                label="Glucose Feed"
            )

            # Plot 4 - Volume, Air, pH, Stirrer Speed
            ax4.set_ylabel(r"Volume / L, Air / L $\cdot$ min$^{-1}$, pH", fontsize=label_font_size)
            ax4y2 = ax4.twinx()
            ax4y2.set_ylabel(r"Stirrer Speed / min$^{-1}$", fontsize=label_font_size)

            ax4.plot(
                self.processor.online_data['time'],
                self.processor.online_data['sVR'],
                color="#27ABCF",
                linestyle="-",
                linewidth=1,
                label="Volume"
            )
            ax4.plot(
                self.processor.online_data['time'],
                self.processor.online_data['spH'],
                color="#8B4513",
                linestyle="-",
                linewidth=1,
                label="pH"
            )
            ax4y2.plot(
                self.processor.online_data['time'][self.processor.valid_stirrer_mask],
                self.processor.online_data['NStirrer'][self.processor.valid_stirrer_mask],
                color="#CD1076",
                linestyle="-",
                linewidth=1,
                label="Stirrer Speed"
            )
            ax4.plot(
                self.processor.online_data['time'][self.processor.valid_aeration_mask],
                self.processor.online_data['FAirIn'][self.processor.valid_aeration_mask],
                color="#0B610B",
                linestyle="-",
                linewidth=1,
                label="Air"
            )

            # Set title and subtitle
            plt.suptitle('Main Culture Simulation', fontsize=title_font_size)
            plt.figtext(
                0.5,
                0.01,
                f"Group 1: Carolin Beck, Ann-Kathrin Debatin, etc., {date.today().strftime('%d/%m/%Y')}",
                fontstyle='italic',
                fontsize=10,
                horizontalalignment='center'
            )

            # Add legends
            for ax in [ax1, ax1y2, ax2, ax2y2, ax3, ax3y2, ax4, ax4y2]:
                handles, labels = ax.get_legend_handles_labels()
                if handles:
                    ax.legend(loc='upper right', fontsize=12)

            # Automatically adjust the layout to avoid overlap
            plt.tight_layout(pad=3)

            # Create a timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_filename = self.plot_dir / f"main_culture_simulation_{timestamp}.png"
            plt.savefig(plot_filename, dpi=self.dpi)
            logger.info(f"Main culture simulation plot saved to {plot_filename}")

            # Optionally, display the plot
            plt.show()
            plt.close(fig)  # Close the figure to free memory
            logger.info("Main culture simulation plots generated successfully.")
        except Exception as e:
            logger.error(f"Error generating main culture simulation plots: {e}")
            raise

    def plot_kla_data(self, df: pd.DataFrame, kla_filename: str) -> None:
        """
        Plot KLA data and save the figure to the plot directory.

        :param df: DataFrame containing KLA data.
        :param kla_filename: Name of the KLA data file for descriptive plotting.
        """
        logger.info(f"Generating KLA data plots for {kla_filename}.")
        try:
            sns.set(style=self.style)
            plt.figure(figsize=self.figsize_kla)

            plot_columns = ['spO2', 'sO2', 'sCO2', 'NStirrer', 'FAirIn', 'FO2In']
            colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']

            for col, color in zip(plot_columns, colors):
                if col in df.columns:
                    plt.plot(df['Time'], df[col], label=f'{col}', color=color)
                else:
                    logger.warning(f"Column '{col}' not found in KLA data and will be skipped.")

            plt.xlabel('Time')
            plt.ylabel('Measurements')
            plt.title(f'Measurement Data Over Time - {kla_filename}')
            plt.legend()
            plt.tight_layout()

            # Extract parameters from filename for descriptive naming
            # Assuming filename format: Daten(klA)400rpm 3L.txt
            parts = kla_filename.replace('.txt', '').split(')')
            if len(parts) > 1:
                rpm_volume = parts[1].strip()
            else:
                rpm_volume = 'unknown'

            # Create a timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Use the rpm and volume in the plot filename
            plot_filename = self.plot_dir / f"kla_data_plot_{rpm_volume}_{timestamp}.png"
            plt.savefig(plot_filename, dpi=self.dpi)
            logger.info(f"KLA data plot saved to {plot_filename}")

            # Optionally, display the plot
            plt.show()
            plt.close()
            logger.info("KLA data plots generated successfully.")
        except Exception as e:
            logger.error(f"Error generating KLA data plots for {kla_filename}: {e}")
            raise
