"""
Download FX tick data from Dukascopy historical data feed.
Supports multiple currency pairs and configurable date ranges.
"""

import argparse
import struct
import lzma
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
import requests
import pandas as pd
from tqdm import tqdm

from utils import (
    setup_logging,
    validate_date_range,
    validate_currency_pair,
    ensure_directory,
    generate_date_range
)

logger = setup_logging(__name__)


class DukascopyDownloader:
    """Download tick data from Dukascopy historical data API."""
    
    BASE_URL = "https://datafeed.dukascopy.com/datafeed"
    
    def __init__(self, pair: str, output_dir: str = "data/raw"):
        """
        Initialize downloader.
        
        Args:
            pair: Currency pair (e.g., 'EURUSD')
            output_dir: Directory to save raw data
        """
        self.pair = validate_currency_pair(pair)
        self.output_dir = output_dir
        ensure_directory(output_dir)
        
    def _get_tick_url(self, dt: datetime, hour: int) -> str:
        """
        Construct URL for tick data file.
        
        Args:
            dt: Date
            hour: Hour of day (0-23)
            
        Returns:
            URL string
        """
        # Dukascopy format: {PAIR}/{YEAR}/{MONTH_0_INDEXED}/{DAY}/{HOUR}h_ticks.bi5
        year = dt.year
        month = dt.month - 1  # Dukascopy uses 0-indexed months
        day = dt.day
        
        url = (
            f"{self.BASE_URL}/{self.pair}/"
            f"{year:04d}/{month:02d}/{day:02d}/"
            f"{hour:02d}h_ticks.bi5"
        )
        return url
    
    def _download_file(self, url: str) -> bytes:
        """
        Download file from URL.
        
        Args:
            url: URL to download
            
        Returns:
            File content as bytes, or None if failed
        """
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                return None
        except Exception as e:
            logger.debug(f"Download failed for {url}: {e}")
            return None
    
    def _decompress_bi5(self, compressed_data: bytes) -> bytes:
        """
        Decompress LZMA-compressed bi5 data.
        
        Args:
            compressed_data: Compressed bytes
            
        Returns:
            Decompressed bytes
        """
        return lzma.decompress(compressed_data)
    
    def _parse_bi5(self, data: bytes, dt: datetime, hour: int) -> pd.DataFrame:
        """
        Parse binary bi5 tick data format.
        
        Bi5 format: Each tick is 20 bytes:
        - timestamp (int32): milliseconds since hour start
        - ask (int32): price * 100000
        - bid (int32): price * 100000
        - ask_volume (float32)
        - bid_volume (float32)
        
        Args:
            data: Binary data
            dt: Date
            hour: Hour
            
        Returns:
            DataFrame with tick data
        """
        if len(data) == 0:
            return pd.DataFrame()
        
        # Each tick is 20 bytes
        chunk_size = 20
        num_ticks = len(data) // chunk_size
        
        ticks = []
        base_time = datetime(dt.year, dt.month, dt.day, hour, 0, 0)
        
        for i in range(num_ticks):
            chunk = data[i * chunk_size:(i + 1) * chunk_size]
            
            # Unpack binary data
            # Format: >IIIff (big-endian: uint32, uint32, uint32, float32, float32)
            timestamp_ms, ask_int, bid_int, ask_vol, bid_vol = struct.unpack('>IIIff', chunk)
            
            # Convert to timestamp
            timestamp = base_time + timedelta(milliseconds=timestamp_ms)
            
            # Convert prices (stored as int * 100000)
            ask = ask_int / 100000.0
            bid = bid_int / 100000.0
            
            ticks.append({
                'timestamp': timestamp,
                'ask': ask,
                'bid': bid,
                'ask_volume': ask_vol,
                'bid_volume': bid_vol
            })
        
        return pd.DataFrame(ticks)
    
    def download_day(self, dt: datetime) -> pd.DataFrame:
        """
        Download all tick data for a single day.
        
        Args:
            dt: Date to download
            
        Returns:
            DataFrame with all ticks for the day
        """
        logger.info(f"Downloading {self.pair} data for {dt.date()}")
        
        day_ticks = []
        
        for hour in range(24):
            url = self._get_tick_url(dt, hour)
            
            # Download compressed file
            compressed_data = self._download_file(url)
            if compressed_data is None:
                continue
            
            # Decompress
            try:
                decompressed_data = self._decompress_bi5(compressed_data)
            except Exception as e:
                logger.warning(f"Failed to decompress {url}: {e}")
                continue
            
            # Parse binary format
            try:
                hour_df = self._parse_bi5(decompressed_data, dt, hour)
                if not hour_df.empty:
                    day_ticks.append(hour_df)
            except Exception as e:
                logger.warning(f"Failed to parse {url}: {e}")
                continue
        
        if not day_ticks:
            logger.warning(f"No data found for {dt.date()}")
            return pd.DataFrame()
        
        # Combine all hours
        day_df = pd.concat(day_ticks, ignore_index=True)
        logger.info(f"Downloaded {len(day_df):,} ticks for {dt.date()}")
        
        return day_df
    
    def download_range(self, start_date: str, end_date: str, save: bool = True) -> pd.DataFrame:
        """
        Download tick data for a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            save: Whether to save to CSV
            
        Returns:
            Combined DataFrame for the entire range
        """
        start_dt, end_dt = validate_date_range(start_date, end_date)
        dates = generate_date_range(start_dt, end_dt)
        
        logger.info(f"Downloading {self.pair} from {start_date} to {end_date} ({len(dates)} days)")
        
        all_ticks = []
        
        for dt in tqdm(dates, desc="Downloading days"):
            day_df = self.download_day(dt)
            if not day_df.empty:
                all_ticks.append(day_df)
        
        if not all_ticks:
            logger.error("No data downloaded!")
            return pd.DataFrame()
        
        # Combine all days
        combined_df = pd.concat(all_ticks, ignore_index=True)
        combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
        
        logger.info(f"Total ticks downloaded: {len(combined_df):,}")
        
        if save:
            # Save to CSV
            filename = f"{self.pair}_{start_date}_{end_date}.csv"
            filepath = os.path.join(self.output_dir, filename)
            combined_df.to_csv(filepath, index=False)
            logger.info(f"Saved to {filepath}")
        
        return combined_df


def main():
    """Command-line interface for data download."""
    parser = argparse.ArgumentParser(description="Download FX tick data from Dukascopy")
    parser.add_argument('--pair', type=str, required=True, help='Currency pair (e.g., EURUSD)')
    parser.add_argument('--start', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--output', type=str, default='data/raw', help='Output directory')
    
    args = parser.parse_args()
    
    downloader = DukascopyDownloader(pair=args.pair, output_dir=args.output)
    downloader.download_range(start_date=args.start, end_date=args.end, save=True)
    
    logger.info("Download complete!")


if __name__ == "__main__":
    main()
