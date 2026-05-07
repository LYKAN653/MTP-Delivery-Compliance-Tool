import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import math
from fuzzywuzzy import fuzz
import warnings
warnings.filterwarnings('ignore')

# Version: 2.1 with MSQ logic, lead time parsing fix, and Item Location mapping by Item Category
print("Sales Order Analyzer v2.1 loading...")

class SalesOrderAnalyzer:
    """
    Analyzes sales order data with lead times, dispatch status, and item locations
    """
    
    def __init__(self):
        self.df_orders = None
        self.df_lead_times = None
        self.df_locations = None
        self.location_map = {}

    # =========================
    # Timestamp extraction utils
    # =========================
    def extract_timestamp(self, text):
        """
        Extract first timestamp from remark text
        Format: "DD MMM YYYY HH:MM:SS (remark)"
        Returns datetime object or None
        """
        if pd.isna(text) or text == '':
            return None
        
        pattern = r'(\d{2}\s+\w{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2})'
        matches = re.findall(pattern, str(text))
        
        if matches:
            try:
                return datetime.strptime(matches[0], '%d %b %Y %H:%M:%S')
            except:
                return None
        return None
    
    def extract_all_timestamps(self, text):
        """
        Extract all timestamps from a remark field
        Format: "DD MMM YYYY HH:MM:SS (remark)"
        Returns list of datetime objects
        """
        if pd.isna(text) or text == '':
            return []
        
        pattern = r'(\d{2}\s+\w{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2})'
        matches = re.findall(pattern, str(text))
        
        timestamps = []
        for match in matches:
            try:
                ts = datetime.strptime(match, '%d %b %Y %H:%M:%S')
                timestamps.append(ts)
            except:
                pass
        
        return sorted(timestamps)
    
    def extract_scheduled_dispatch_date(self, text):
        """
        Extract scheduled dispatch date from PPC remarks
        Format: "Dispatch plan : DD/MM/YY"
        Returns datetime object or None
        """
        if pd.isna(text) or text == '':
            return None
        
        pattern = r'dispatch\s+plan\s*:\s*(\d{1,2})/(\d{1,2})/(\d{2,4})'
        matches = re.findall(pattern, str(text), re.IGNORECASE)
        
        if matches:
            try:
                day, month, year = matches[-1]
                year = int(year)
                if year < 100:
                    year = 2000 + year if year < 50 else 1900 + year
                return datetime(year, int(month), int(day))
            except:
                return None
        return None
    
    def extract_all_remarks_timestamps(self, row):
        """
        Extract all timestamps from all remark columns and arrange chronologically.
        Returns: list of tuples [(timestamp, remark_column, remark_text_snippet), ...]
        """
        all_timestamps = []
        remark_columns = ['Cost Approval Remark', 'Account Remark', 'PPC Remark', 'Dispatch Remark']
        
        for remark_col in remark_columns:
            remark_text = row.get(remark_col, '')
            if pd.isna(remark_text) or remark_text == '':
                continue
            
            pattern = r'(\d{2}\s+\w{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2})'
            matches = re.findall(pattern, str(remark_text))
            
            for match in matches:
                try:
                    ts = datetime.strptime(match, '%d %b %Y %H:%M:%S')
                    all_timestamps.append((ts, remark_col, str(remark_text)[:100]))
                except:
                    continue
        
        all_timestamps.sort(key=lambda x: x[0])
        return all_timestamps
    
    # =========================
    # Bottleneck logic
    # =========================
    def identify_bottleneck_stage_v2(self, row):
        """
        Identify bottleneck stage based on largest consecutive timestamp gap.
        Returns the remark column where the largest gap ends.
        """
        details = self.get_bottleneck_gap_details(row)
        return details.get('Bottleneck_Stage')

    def get_bottleneck_gap_details(self, row):
        """
        Analyze all remark timestamps for an order, identify the largest gap,
        and classify the bottleneck stage and department.
        """
        all_timestamps = self.extract_all_remarks_timestamps(row)
        if len(all_timestamps) < 2:
            return {
                'Bottleneck_Gap_Start_Stage': None,
                'Bottleneck_Gap_End_Stage': None,
                'Bottleneck_Gap_Start_TS': None,
                'Bottleneck_Gap_End_TS': None,
                'Bottleneck_Gap_Days': None,
                'Bottleneck_Stage': None,
                'Bottleneck_Department': None,
                'Bottleneck_Detail': None,
                'Bottleneck_Scheduled': False,
                'Bottleneck_Scheduled_Lag_Days': None
            }

        stage_mapping = {
            'Cost Approval Remark': 'Cost Approval',
            'Account Remark': 'Account Approval',
            'PPC Remark': 'PPC',
            'Dispatch Remark': 'Dispatch'
        }

        max_gap = 0
        gap_start = gap_end = None
        gap_start_stage = gap_end_stage = None
        gap_start_text = gap_end_text = None

        for i in range(len(all_timestamps) - 1):
            current = all_timestamps[i]
            next_item = all_timestamps[i + 1]
            gap_days = (next_item[0] - current[0]).total_seconds() / (3600 * 24)
            if gap_days > max_gap:
                max_gap = gap_days
                gap_start = current[0]
                gap_end = next_item[0]
                gap_start_stage = stage_mapping.get(current[1], current[1])
                gap_end_stage = stage_mapping.get(next_item[1], next_item[1])
                gap_start_text = current[2]
                gap_end_text = next_item[2]

        bottleneck_stage = gap_end_stage
        bottleneck_department = None
        special_label = None
        bottleneck_detail = f"Gap between {gap_start_stage} and {gap_end_stage}"
        bottleneck_scheduled = False
        scheduled_lag = None

        ppc_remark = str(row.get('PPC Remark', '')).lower()
        scheduling_keywords = ['schedule', 'batch', 'dispatch plan', 'dispatch batch', 'scheduled']
        has_scheduling_keyword = any(keyword in ppc_remark for keyword in scheduling_keywords)
        schedule_date = row.get('Scheduled_Dispatch_Date')
        ppc_reference_ts = None
        if pd.notna(row.get('PPC_Last_Timestamp')):
            ppc_reference_ts = row.get('PPC_Last_Timestamp')
        elif pd.notna(row.get('PPC_First_Timestamp')):
            ppc_reference_ts = row.get('PPC_First_Timestamp')
        elif len(row.get('PPC_Timestamps', [])) > 0:
            ppc_reference_ts = row['PPC_Timestamps'][0]

        if has_scheduling_keyword and pd.notna(schedule_date) and ppc_reference_ts is not None:
            if schedule_date.date() > ppc_reference_ts.date():
                bottleneck_scheduled = True
                scheduled_lag = (schedule_date.date() - ppc_reference_ts.date()).days
                special_label = 'Scheduled Dispatch'
            elif schedule_date.date() == ppc_reference_ts.date():
                bottleneck_scheduled = False
            else:
                bottleneck_scheduled = False

        material_ready = 'material is ready' in ppc_remark or 'ready for dispatch' in ppc_remark
        if material_ready and gap_start_stage == 'PPC':
            special_label = 'Hold or Dispatch'

        if special_label == 'Hold or Dispatch':
            bottleneck_stage = 'Hold or Dispatch'
            bottleneck_department = 'Hold or Dispatch'
        elif special_label == 'Scheduled Dispatch':
            bottleneck_stage = 'Scheduled Dispatch'
            bottleneck_department = 'Scheduled Dispatch'
        else:
            if bottleneck_stage == 'Account Approval':
                bottleneck_department = 'Account Approval'
            elif bottleneck_stage == 'Cost Approval':
                bottleneck_department = 'Cost Approval'
            elif bottleneck_stage == 'Dispatch':
                bottleneck_department = 'Dispatch'
            elif bottleneck_stage == 'PPC':
                if gap_start_stage == 'Account Approval':
                    bottleneck_department = 'PPC Planning'
                else:
                    bottleneck_department = 'PPC Production'
            else:
                bottleneck_department = bottleneck_stage

        return {
            'Bottleneck_Gap_Start_Stage': gap_start_stage,
            'Bottleneck_Gap_End_Stage': gap_end_stage,
            'Bottleneck_Gap_Start_TS': gap_start,
            'Bottleneck_Gap_End_TS': gap_end,
            'Bottleneck_Gap_Days': round(max_gap, 2) if max_gap > 0 else None,
            'Bottleneck_Stage': bottleneck_stage,
            'Bottleneck_Department': bottleneck_department,
            'Bottleneck_Detail': bottleneck_detail,
            'Bottleneck_Scheduled': bottleneck_scheduled,
            'Bottleneck_Scheduled_Lag_Days': scheduled_lag
        }
    
    def get_max_gap_between_remarks(self, row):
        """
        Get the maximum gap (in days) between consecutive timestamps across all remarks.
        """
        all_timestamps = self.extract_all_remarks_timestamps(row)
        if len(all_timestamps) < 2:
            return None
        max_gap = 0
        for i in range(len(all_timestamps) - 1):
            gap_days = (all_timestamps[i + 1][0] - all_timestamps[i][0]).total_seconds() / (3600 * 24)
            max_gap = max(max_gap, gap_days)
        return round(max_gap, 2) if max_gap > 0 else None

    # =========================
    # Matching & lead-time logic
    # =========================
    def fuzzy_match_item(self, item_desc, reference_items, threshold=60):
        """
        Perform fuzzy matching for item description
        Returns best match, lead time, and item group
        """
        if pd.isna(item_desc):
            return None, None, None
        
        best_match = None
        best_score = 0
        best_lead_time = None
        best_item_group = None
        
        for idx, ref_item in reference_items.iterrows():
            score = fuzz.ratio(str(item_desc).lower(), 
                             str(ref_item.get('Item Description', '')).lower())
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = ref_item.get('Item Description')
                best_lead_time = ref_item.get('Lead Time')
                best_item_group = ref_item.get('Item Categories')
                if pd.isna(best_item_group) or best_item_group == '':
                    best_item_group = ref_item.get('Item Group')
                if pd.isna(best_item_group) or best_item_group == '':
                    best_item_group = ref_item.get('Item Category')
        
        return best_match, best_lead_time, best_item_group
    
    def load_data(self, orders_file1, orders_file2, lead_times_file, locations_file=None):
        """
        Load orders, lead times, and locations (mapping) data
        """
        print("Loading data files...")
        
        # Load sales order data from both sheets
        df1 = pd.read_excel(orders_file1)
        df2 = pd.read_excel(orders_file2)
        self.df_orders = pd.concat([df1, df2], ignore_index=True)
        
        # Load lead times from all relevant sheets
        try:
            excel_file = pd.ExcelFile(lead_times_file)
            sheets_to_load = ['CONCEPT ', 'MPPL', 'Lashing', 'Sheet1', 'Sheet2']
            lead_time_frames = []

            for sheet_name in sheets_to_load:
                if sheet_name not in excel_file.sheet_names:
                    continue

                df_sheet = pd.read_excel(excel_file, sheet_name=sheet_name)
                df_sheet['Lead_Time_Source'] = sheet_name

                # Normalize tag lookup columns
                if 'Tag No' in df_sheet.columns and 'Item Number' not in df_sheet.columns:
                    df_sheet['Item Number'] = df_sheet['Tag No']

                if sheet_name == 'MPPL' and 'Lead Time' in df_sheet.columns:
                    df_sheet['Lead Time'] = pd.to_numeric(df_sheet['Lead Time'], errors='coerce') / 24.0

                if 'Lead time for production' in df_sheet.columns:
                    df_sheet['Lead Time'] = df_sheet['Lead time for production']

                if 'Lead Time.1' in df_sheet.columns and 'Lead Time' not in df_sheet.columns:
                    df_sheet['Lead Time'] = df_sheet['Lead Time.1']

                # Normalize category fields for sheets that use Item Category instead of Item Group
                if 'Item Categories' in df_sheet.columns and 'Item Group' not in df_sheet.columns:
                    df_sheet['Item Group'] = df_sheet['Item Categories']
                elif 'Item Category' in df_sheet.columns and 'Item Group' not in df_sheet.columns:
                    df_sheet['Item Group'] = df_sheet['Item Category']

                lead_time_frames.append(df_sheet)

            if lead_time_frames:
                self.df_lead_times = pd.concat(lead_time_frames, ignore_index=True)
            else:
                raise ValueError('No lead time sheets found')
            
        except Exception as e:
            print(f"Error loading lead times: {e}")
            # Fallback to loading without sheet specification (old behavior)
            self.df_lead_times = pd.read_excel(lead_times_file)
            self.df_lead_times['Lead_Time_Source'] = 'unknown'
        
        print(f"Loaded {len(self.df_orders)} order records")
        print(f"Loaded {len(self.df_lead_times)} lead time records")
        if 'Lead_Time_Source' in self.df_lead_times.columns:
            print(f"Lead time sources: {self.df_lead_times['Lead_Time_Source'].value_counts().to_dict()}")
        
        # Load locations mapping
        self.location_map = {}
        try:
            if locations_file is None:
                locations_file = 'Location file.xlsx'  # fallback

            self.df_locations = pd.read_excel(locations_file)
            print(f"Loaded {len(self.df_locations)} location records")

            # Normalize column names and content
            self.df_locations.columns = [c.strip() for c in self.df_locations.columns]

            # Identify category key column in the locations file
            candidate_category_cols = ['Item Categories', 'Item Group', 'Item Category']
            cat_col = next((c for c in candidate_category_cols if c in self.df_locations.columns), None)

            if cat_col is None or 'Location' not in self.df_locations.columns:
                print("Warning: Could not identify category or 'Location' column in locations file")
            else:
                self.df_locations[cat_col] = (
                    self.df_locations[cat_col]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                )
                # Build dictionary mapping category -> location
                self.location_map = dict(
                    self.df_locations[[cat_col, 'Location']].dropna().drop_duplicates().values
                )
                print(f"Built location map with {len(self.location_map)} categories")

        except Exception as e:
            print(f"Error loading locations file: {e}")
            self.df_locations = pd.DataFrame()
            self.location_map = {}
    
    def parse_lead_time(self, lead_time_str):
        """
        Parse lead time string which might be:
        - "5"
        - "2 to 3 days" (range, case-insensitive)
        - "5 days"
        Returns the numeric value (for ranges, takes the first number)
        """
        if pd.isna(lead_time_str) or lead_time_str == '':
            return None
        
        lead_time_str = str(lead_time_str).strip()
        numbers = re.findall(r'\d+\.?\d*', lead_time_str)
        if numbers:
            return float(numbers[0])
        return None
    
    def calculate_msq_based_lead_time(self, item_data, order_quantity):
        """
        Calculate lead time based on MSQ (Minimum Stock Quantity) logic.
        """
        base_lead_time = self.parse_lead_time(item_data.get('Lead Time'))
        if base_lead_time is None:
            base_lead_time = 2  # Default for standard items
        
        msq = item_data.get('Confirmed MSQ if any')
        if pd.isna(msq) or msq == '' or msq == 0:
            return base_lead_time
        
        try:
            msq = float(msq)
        except (ValueError, TypeError):
            return base_lead_time
        
        if msq == 0:
            return base_lead_time
        
        try:
            order_qty = float(order_quantity) if pd.notna(order_quantity) else 0
        except (ValueError, TypeError):
            return base_lead_time
        
        if order_qty <= msq:
            return 1
        
        batch_qty = item_data.get('Batch production quantity per day')
        if pd.isna(batch_qty) or batch_qty == '' or batch_qty == 0:
            return base_lead_time
        
        try:
            batch_qty = float(batch_qty)
        except (ValueError, TypeError):
            return base_lead_time
        
        if batch_qty == 0:
            return base_lead_time
        
        if batch_qty >= order_qty:
            return base_lead_time
        
        num_batches = math.ceil(order_qty / batch_qty)
        calculated_lead_time = num_batches * base_lead_time
        return calculated_lead_time
    
    def lookup_location(self, item_category):
        """
        Fallback location lookup by item category using loaded locations data.
        Returns location if found, otherwise 'Location not found'.
        """
        if pd.isna(item_category) or item_category == '' or item_category == 'Category not found':
            return 'Location not found'

        # Prefer dictionary map if available
        if self.location_map:
            key = str(item_category).strip().lower()
            return self.location_map.get(key, 'Location not found')

        # Fallback to scanning df_locations (legacy)
        if not isinstance(self.df_locations, pd.DataFrame) or self.df_locations.empty:
            return 'Location not found'

        location_column = None
        if 'Item Categories' in self.df_locations.columns:
            location_column = 'Item Categories'
        elif 'Item Group' in self.df_locations.columns:
            location_column = 'Item Group'
        elif 'Item Category' in self.df_locations.columns:
            location_column = 'Item Category'
        else:
            return 'Location not found'

        match_locations = self.df_locations[
            self.df_locations[location_column].astype(str).str.lower() == str(item_category).lower()
        ]
        
        if not match_locations.empty:
            location = match_locations.iloc[0].get('Location')
            if pd.notna(location) and location != '':
                return location
        
        return 'Location not found'
    
    def lookup_lead_time(self, row):
        """
        Look up lead time for an item from lead times data with MSQ logic:
        1. Exact match on Item Description
        2. Exact match on Tag No to Item Number (if non-generic)
        3. Fuzzy match on Item Description
        4. Apply MSQ-based calculation if MSQ data is available
        """
        tag_no = row.get('Tag No')
        item_desc = row['Item Description']
        order_qty = row.get('Qty')
        
        # Try exact match on Item Description FIRST
        match_lead_times = self.df_lead_times[
            self.df_lead_times['Item Description'].str.lower() == str(item_desc).lower()
        ]
        
        if not match_lead_times.empty:
            item_data = match_lead_times.iloc[0]
            if pd.notna(order_qty):
                lead_time = self.calculate_msq_based_lead_time(item_data, order_qty)
                if lead_time is not None:
                    return lead_time
            lead_time = self.parse_lead_time(item_data.get('Lead Time'))
            if lead_time is not None:
                return lead_time
        
        # Try exact match on Tag No to Item Number (if tag is specific)
        if pd.notna(tag_no) and str(tag_no).lower() not in ['cust.', 'cust', 'custom', 'n/a', 'na', 'unknown']:
            match_lead_times = self.df_lead_times[
                self.df_lead_times['Item Number'].astype(str).str.lower() == str(tag_no).lower()
            ]
            if not match_lead_times.empty:
                item_data = match_lead_times.iloc[0]
                if pd.notna(order_qty):
                    lead_time = self.calculate_msq_based_lead_time(item_data, order_qty)
                    if lead_time is not None:
                        return lead_time
                lead_time = self.parse_lead_time(item_data.get('Lead Time'))
                if lead_time is not None:
                    return lead_time
        
        # Try fuzzy match on Item Description
        best_match, best_lead_time, best_item_group = self.fuzzy_match_item(item_desc, self.df_lead_times)
        if best_match is not None:
            match_lead_times = self.df_lead_times[
                self.df_lead_times['Item Description'].str.lower() == str(best_match).lower()
            ]
            if not match_lead_times.empty:
                item_data = match_lead_times.iloc[0]
                if pd.notna(order_qty):
                    lead_time = self.calculate_msq_based_lead_time(item_data, order_qty)
                    if lead_time is not None:
                        return lead_time
                return self.parse_lead_time(best_lead_time)
        
        return "Lead time not found"
    
    def lookup_item_category(self, row):
        """
        Determine item category (Item Group) using:
        1. Exact match on Item Description
        2. Exact match on Tag No to Item Number (if non-generic)
        3. Fuzzy match on Item Description
        """
        tag_no = row.get('Tag No')
        item_desc = row['Item Description']
        
        # Exact match on Item Description
        match_lead_times = self.df_lead_times[
            self.df_lead_times['Item Description'].str.lower() == str(item_desc).lower()
        ]
        if not match_lead_times.empty:
            row_category = match_lead_times.iloc[0].get('Item Categories')
            if pd.isna(row_category) or row_category == '':
                row_category = match_lead_times.iloc[0].get('Item Group')
            if pd.isna(row_category) or row_category == '':
                row_category = match_lead_times.iloc[0].get('Item Category')
            category = row_category
            if pd.notna(category) and category != '':
                return category
        
        # Exact match on Tag No to Item Number (if specific)
        if pd.notna(tag_no) and str(tag_no).lower() not in ['cust.', 'cust', 'custom', 'n/a', 'na', 'unknown']:
            match_lead_times = self.df_lead_times[
                self.df_lead_times['Item Number'].astype(str).str.lower() == str(tag_no).lower()
            ]
            if not match_lead_times.empty:
                row_category = match_lead_times.iloc[0].get('Item Categories')
                if pd.isna(row_category) or row_category == '':
                    row_category = match_lead_times.iloc[0].get('Item Group')
                if pd.isna(row_category) or row_category == '':
                    row_category = match_lead_times.iloc[0].get('Item Category')
                category = row_category
                if pd.notna(category) and category != '':
                    return category
        
        # Fuzzy match on Item Description
        best_match, _, best_item_group = self.fuzzy_match_item(item_desc, self.df_lead_times)
        if best_match is not None and best_item_group is not None:
            return best_item_group
        
        return "Category not found"
    
    # =========================
    # Calculations & statuses
    # =========================
    def calculate_time_differences(self):
        """
        Calculate all required timestamp differences and derive locations
        """
        print("Calculating timestamp differences...")
        
        # Parse OA Date - format "DD MMM YYYY HH:MM:SS:milliseconds"
        def parse_oa_date(date_str):
            if pd.isna(date_str):
                return None
            try:
                date_str = str(date_str).rsplit(':', 1)[0]  # Remove last :000
                return datetime.strptime(date_str, '%d %b %Y %H:%M:%S')
            except:
                return None
        
        self.df_orders['OA_Date_Parsed'] = self.df_orders['OA Date'].apply(parse_oa_date)
        
        # Lead time lookup
        print("Looking up lead times...")
        self.df_orders['Lead_Time_Days'] = self.df_orders.apply(self.lookup_lead_time, axis=1)
        
        # Item category lookup
        print("Looking up item categories...")
        self.df_orders['Item_Category'] = self.df_orders.apply(self.lookup_item_category, axis=1)
        
        # Item location mapping from Item_Category (vectorized)
        print("Looking up item locations...")
        self.df_orders['Item_Category_Key'] = (
            self.df_orders['Item_Category']
            .astype(str)
            .str.strip()
            .str.lower()
        )
        if getattr(self, 'location_map', None):
            self.df_orders['Item_Location'] = self.df_orders['Item_Category_Key'].map(self.location_map)
            self.df_orders['Item_Location'] = self.df_orders['Item_Location'].fillna('Location not found')
        else:
            # Fallback to legacy row-wise function
            self.df_orders['Item_Location'] = self.df_orders['Item_Category'].apply(self.lookup_location)
        
        # Ideal dispatch date (only for numeric lead times)
        def calc_ideal_dispatch(row):
            if pd.notna(row['OA_Date_Parsed']) and isinstance(row['Lead_Time_Days'], (int, float)):
                try:
                    return row['OA_Date_Parsed'] + timedelta(days=float(row['Lead_Time_Days']))
                except:
                    return None
            return None
        
        self.df_orders['Ideal_Dispatch_Date'] = self.df_orders.apply(calc_ideal_dispatch, axis=1)
        
        # Account timestamps & max diff
        self.df_orders['Account_Timestamps'] = self.df_orders['Account Remark'].apply(self.extract_all_timestamps)
        
        def calc_max_account_diff(timestamps):
            if len(timestamps) < 2:
                return None, None, None
            max_diff = 0
            max_diff_start = None
            max_diff_end = None
            for i in range(len(timestamps) - 1):
                diff = (timestamps[i + 1] - timestamps[i]).total_seconds() / (3600 * 24)
                if diff > max_diff:
                    max_diff = diff
                    max_diff_start = timestamps[i]
                    max_diff_end = timestamps[i + 1]
            return round(max_diff, 2) if max_diff > 0 else None, max_diff_start, max_diff_end
        
        self.df_orders[['Max_Account_Diff_Days', 'Max_Account_Diff_Start_TS', 'Max_Account_Diff_End_TS']] = \
            self.df_orders['Account_Timestamps'].apply(lambda x: pd.Series(calc_max_account_diff(x)))
        
        # Extract timestamps from remark columns
        print("Parsing remark timestamps...")
        self.df_orders['Cost_Approval_Timestamp'] = self.df_orders['Cost Approval Remark'].apply(self.extract_timestamp)
        self.df_orders['Account_Remark_Timestamp'] = self.df_orders['Account_Timestamps'].apply(
            lambda x: x[0] if len(x) > 0 else None
        )
        self.df_orders['Dispatch_Remark_Timestamp'] = self.df_orders['Dispatch Remark'].apply(self.extract_timestamp)
        
        # PPC timestamps
        self.df_orders['PPC_Timestamps'] = self.df_orders['PPC Remark'].apply(self.extract_all_timestamps)
        self.df_orders['Scheduled_Dispatch_Date'] = self.df_orders['PPC Remark'].apply(self.extract_scheduled_dispatch_date)
        
        print("Calculating time differences...")
        # a. OA Date to Ideal Dispatch Date
        self.df_orders['Diff_OA_to_Ideal_Dispatch'] = self.df_orders.apply(
            lambda row: (row['Ideal_Dispatch_Date'] - row['OA_Date_Parsed']).days 
            if pd.notna(row['Ideal_Dispatch_Date']) and pd.notna(row['OA_Date_Parsed']) 
            else None,
            axis=1
        )
        
        # b. OA Date to Cost Approval
        self.df_orders['Diff_OA_to_Cost_Approval'] = self.df_orders.apply(
            lambda row: round((row['Cost_Approval_Timestamp'] - row['OA_Date_Parsed']).total_seconds() / (3600 * 24), 2)
            if pd.notna(row['Cost_Approval_Timestamp']) and pd.notna(row['OA_Date_Parsed']) and pd.notna(row['Cost Approval Remark'])
            else None,
            axis=1
        )
        
        # c. OA Date to Account Remark
        self.df_orders['Diff_OA_to_Account'] = self.df_orders.apply(
            lambda row: round((row['Account_Remark_Timestamp'] - row['OA_Date_Parsed']).total_seconds() / (3600 * 24), 2)
            if pd.notna(row['Account_Remark_Timestamp']) and pd.notna(row['OA_Date_Parsed']) 
            else None,
            axis=1
        )
        
        # d. Cost Approval to Account Remark
        self.df_orders['Diff_Cost_to_Account'] = self.df_orders.apply(
            lambda row: round((row['Account_Remark_Timestamp'] - row['Cost_Approval_Timestamp']).total_seconds() / (3600 * 24), 2)
            if pd.notna(row['Account_Remark_Timestamp']) and pd.notna(row['Cost_Approval_Timestamp']) 
            else None,
            axis=1
        )
        
        # e. Account Remark to First PPC Remark
        self.df_orders['Diff_Account_to_PPC_First'] = self.df_orders.apply(
            lambda row: round((row['PPC_Timestamps'][0] - row['Account_Remark_Timestamp']).total_seconds() / (3600 * 24), 2)
            if len(row['PPC_Timestamps']) > 0 and pd.notna(row['Account_Remark_Timestamp']) 
            else None,
            axis=1
        )
        
        # f. PPC timestamp columns and differences
        max_ppc_timestamps = self.df_orders['PPC_Timestamps'].apply(len).max()
        for i in range(max_ppc_timestamps):
            self.df_orders[f'PPC_Timestamp_{i+1}'] = self.df_orders['PPC_Timestamps'].apply(
                lambda x: x[i] if len(x) > i else None
            )
        for i in range(max_ppc_timestamps - 1):
            self.df_orders[f'Diff_PPC_{i+1}_to_PPC_{i+2}'] = self.df_orders.apply(
                lambda row: round((row[f'PPC_Timestamp_{i+2}'] - row[f'PPC_Timestamp_{i+1}']).total_seconds() / (3600 * 24), 2)
                if pd.notna(row[f'PPC_Timestamp_{i+2}']) and pd.notna(row[f'PPC_Timestamp_{i+1}']) 
                else None,
                axis=1
            )
        
        # g. Last PPC Timestamp to Dispatch Remark
        self.df_orders['PPC_Last_Timestamp'] = self.df_orders['PPC_Timestamps'].apply(
            lambda x: x[-1] if len(x) > 0 else None
        )
        self.df_orders['Diff_PPC_Last_to_Dispatch'] = self.df_orders.apply(
            lambda row: round((row['Dispatch_Remark_Timestamp'] - row['PPC_Last_Timestamp']).total_seconds() / (3600 * 24), 2)
            if pd.notna(row['Dispatch_Remark_Timestamp']) and pd.notna(row['PPC_Last_Timestamp']) 
            else None,
            axis=1
        )
        
        # h. OA Date to Dispatch Remark
        self.df_orders['Diff_OA_to_Dispatch'] = self.df_orders.apply(
            lambda row: round((row['Dispatch_Remark_Timestamp'] - row['OA_Date_Parsed']).days, 2)
            if pd.notna(row['Dispatch_Remark_Timestamp']) and pd.notna(row['OA_Date_Parsed']) 
            else None,
            axis=1
        )
        
        # i. PPC First Remark to Dispatch Date
        self.df_orders['PPC_First_Timestamp'] = self.df_orders['PPC_Timestamps'].apply(
            lambda x: x[0] if len(x) > 0 else None
        )
        self.df_orders['Diff_PPC_First_to_Dispatch'] = self.df_orders.apply(
            lambda row: round((row['Dispatch_Remark_Timestamp'] - row['PPC_First_Timestamp']).total_seconds() / (3600 * 24), 2)
            if pd.notna(row['Dispatch_Remark_Timestamp']) and pd.notna(row['PPC_First_Timestamp']) 
            else None,
            axis=1
        )
    
    def export_to_excel(self, output_file):
        """
        Export the analyzed data to an Excel file
        """
        if self.df_orders is not None:
            self.df_orders.to_excel(output_file, index=False)
            print(f"Data exported to {output_file}")
            return True
        else:
            print("No data to export")
            return False


# =======================
# GUI Application
# =======================
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    import os
    
    class SalesOrderAnalyzerApp:
        def __init__(self, root):
            self.root = root
            self.root.title("Sales Order Analyzer v2.1")
            self.root.geometry("700x600")
            self.analyzer = SalesOrderAnalyzer()
            
            # Variables to store file paths
            self.orders_file = tk.StringVar()
            self.location_file = tk.StringVar()
            self.lead_times_path = tk.StringVar(value="Lead Time file.xlsx")  # Default path
            
            self.build_gui()
        
        def build_gui(self):
            # Title
            title = tk.Label(self.root, text="Sales Order Analyzer v2.1", 
                           font=("Arial", 16, "bold"), pady=10)
            title.pack()
            
            # Instructions
            instructions = tk.Label(self.root, text="Upload input files and configure lead times location",
                                  font=("Arial", 10), fg="gray")
            instructions.pack()
            
            # Frame for Orders File
            orders_frame = tk.LabelFrame(self.root, text="Sales Order File *", padx=10, pady=10)
            orders_frame.pack(fill="x", padx=10, pady=5)
            
            self.orders_entry = tk.Entry(orders_frame, textvariable=self.orders_file, width=60)
            self.orders_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
            
            orders_btn = tk.Button(orders_frame, text="Browse", 
                                 command=lambda: self.select_file(self.orders_file, "Sales Order"))
            orders_btn.pack(side=tk.LEFT, padx=5)
            
            # Frame for Location File
            location_frame = tk.LabelFrame(self.root, text="Location File *", padx=10, pady=10)
            location_frame.pack(fill="x", padx=10, pady=5)
            
            self.location_entry = tk.Entry(location_frame, textvariable=self.location_file, width=60)
            self.location_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
            
            location_btn = tk.Button(location_frame, text="Browse", 
                                   command=lambda: self.select_file(self.location_file, "Location"))
            location_btn.pack(side=tk.LEFT, padx=5)
            
            # Frame for Lead Times File Path
            lead_frame = tk.LabelFrame(self.root, text="Lead Times File Path", padx=10, pady=10)
            lead_frame.pack(fill="x", padx=10, pady=5)
            
            lead_label = tk.Label(lead_frame, text="(Leave default if in same folder as .exe)", 
                                font=("Arial", 9), fg="gray")
            lead_label.pack(anchor="w")
            
            self.lead_entry = tk.Entry(lead_frame, textvariable=self.lead_times_path, width=60)
            self.lead_entry.pack(fill="x", padx=5, pady=5)
            
            lead_btn = tk.Button(lead_frame, text="Browse", 
                               command=lambda: self.select_file(self.lead_times_path, "Lead Times"))
            lead_btn.pack(anchor="w", padx=5)
            
            # Frame for output file
            output_frame = tk.LabelFrame(self.root, text="Output File Location", padx=10, pady=10)
            output_frame.pack(fill="x", padx=10, pady=5)
            
            self.output_file = tk.StringVar(value="Analysis_Output.xlsx")
            
            output_label = tk.Label(output_frame, text="Output filename:")
            output_label.pack(anchor="w")
            
            self.output_entry = tk.Entry(output_frame, textvariable=self.output_file, width=60)
            self.output_entry.pack(fill="x", padx=5, pady=5)
            
            output_btn = tk.Button(output_frame, text="Choose Location", 
                                 command=self.select_output_file)
            output_btn.pack(anchor="w", padx=5)
            
            # Buttons frame
            button_frame = tk.Frame(self.root, pady=20)
            button_frame.pack(fill="x")
            
            run_btn = tk.Button(button_frame, text="Run Analysis", 
                              command=self.run_analysis, width=20, 
                              bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
            run_btn.pack(side=tk.LEFT, padx=10)
            
            clear_btn = tk.Button(button_frame, text="Clear All", 
                                command=self.clear_all, width=20)
            clear_btn.pack(side=tk.LEFT, padx=10)
            
            # Status bar
            self.status = tk.StringVar(value="Ready")
            status_bar = tk.Label(self.root, textvariable=self.status, 
                                bd=1, relief=tk.SUNKEN, anchor=tk.W)
            status_bar.pack(fill="x", side=tk.BOTTOM)
        
        def select_file(self, var, file_type):
            """Open file dialog"""
            filetypes = [("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            filename = filedialog.askopenfilename(
                title=f"Select {file_type} File",
                filetypes=filetypes
            )
            if filename:
                var.set(filename)
        
        def select_output_file(self):
            """Save file dialog"""
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile="Analysis_Output.xlsx"
            )
            if filename:
                self.output_file.set(filename)
        
        def clear_all(self):
            """Clear all fields"""
            self.orders_file.set("")
            self.location_file.set("")
            self.lead_times_path.set("Lead Time file.xlsx")
            self.output_file.set("Analysis_Output.xlsx")
            self.status.set("Ready")
        
        def run_analysis(self):
            """Run the analysis"""
            orders_file = self.orders_file.get().strip()
            location_file = self.location_file.get().strip()
            lead_times_file = self.lead_times_path.get().strip()
            output_file = self.output_file.get().strip()
            
            # Validation
            if not orders_file:
                messagebox.showerror("Error", "Please select Sales Order file")
                return
            
            if not location_file:
                messagebox.showerror("Error", "Please select Location file")
                return
            
            if not lead_times_file:
                messagebox.showerror("Error", "Please specify Lead Times file path")
                return
            
            if not output_file:
                messagebox.showerror("Error", "Please specify output file path")
                return
            
            # Check files exist
            if not os.path.exists(orders_file):
                messagebox.showerror("Error", f"Sales Order file not found:\n{orders_file}")
                return
            
            if not os.path.exists(location_file):
                messagebox.showerror("Error", f"Location file not found:\n{location_file}")
                return
            
            if not os.path.exists(lead_times_file):
                messagebox.showerror("Error", f"Lead Times file not found:\n{lead_times_file}")
                return
            
            try:
                self.status.set("Loading files...")
                self.root.update()
                
                # Load data
                self.analyzer.load_data(orders_file, orders_file, lead_times_file, location_file)
                
                self.status.set("Calculating time differences...")
                self.root.update()
                
                # Calculate
                self.analyzer.calculate_time_differences()
                
                self.status.set("Exporting results...")
                self.root.update()
                
                # Export
                if self.analyzer.export_to_excel(output_file):
                    self.status.set("Analysis complete!")
                    messagebox.showinfo("Success", 
                        f"Analysis completed successfully!\n\nOutput saved to:\n{output_file}")
                else:
                    messagebox.showerror("Error", "Failed to export results")
                    self.status.set("Error during export")
                    
            except Exception as e:
                self.status.set("Error during analysis")
                messagebox.showerror("Error", f"Analysis failed:\n\n{str(e)}")
                print(f"Error: {e}")
    
    # Create and run the application
    root = tk.Tk()
    app = SalesOrderAnalyzerApp(root)
    root.mainloop()
    

