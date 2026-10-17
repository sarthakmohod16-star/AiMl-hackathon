"""Historical Business Data Processing and Validation Service."""

import csv
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd

from app.schemas.upload import (
    UploadDetailResponse,
    UploadRowError,
    UploadStatus,
    UploadSummaryMetrics,
)

logger = logging.getLogger("biztwin.upload_service")


class UploadProcessingError(Exception):
    """Raised when an uploaded file cannot be parsed or decoded."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# Column normalization aliases
COLUMN_ALIASES: Dict[str, Set[str]] = {
    "date": {"date", "month", "period", "timestamp", "year_month", "billing_period"},
    "revenue": {"revenue", "sales", "turnover", "total_revenue", "income", "gross_revenue"},
    "operating_expenses": {"operating_expenses", "expenses", "opex", "total_expenses", "costs", "overhead"},
    "customers": {"customers", "customer_count", "footfall", "orders", "transactions", "visitors"},
    "cogs": {"cogs", "inventory_cost", "cost_of_goods_sold", "raw_materials"},
}


def normalize_header(header: str) -> Optional[str]:
    """Map a raw column header to standard field name."""
    clean = header.strip().lower().replace(" ", "_").replace("-", "_")
    for standard_name, aliases in COLUMN_ALIASES.items():
        if clean in aliases or clean == standard_name:
            return standard_name
    return None


def parse_date_value(raw: Any) -> Optional[str]:
    """Attempt to parse date strings into ISO format YYYY-MM or YYYY-MM-DD."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None

    # Handle pandas Timestamp or datetime objects
    if isinstance(raw, (datetime, pd.Timestamp)):
        return raw.strftime("%Y-%m-%d")

    # Common formats
    date_formats = [
        "%Y-%m-%d",
        "%Y-%m",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%b %Y",
        "%B %Y",
        "%m-%Y",
        "%m/%Y",
    ]
    for fmt in date_formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d") if "%d" in fmt else dt.strftime("%Y-%m")
        except ValueError:
            continue
    return None


class UploadService:
    """Service responsible for validating and parsing business history spreadsheets."""

    ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

    @classmethod
    def validate_file_metadata(cls, filename: str, content: bytes, max_bytes: int) -> str:
        """Validate file extension and size constraints."""
        clean_name = Path(filename).name
        ext = Path(clean_name).suffix.lower()

        if ext not in cls.ALLOWED_EXTENSIONS:
            raise UploadProcessingError(
                f"Unsupported file format '{ext}'. Allowed formats: CSV (.csv) or Excel (.xlsx, .xls)."
            )

        if len(content) == 0:
            raise UploadProcessingError("Uploaded file is empty (0 bytes).")

        if len(content) > max_bytes:
            max_mb = max_bytes // (1024 * 1024)
            raise UploadProcessingError(
                f"File size ({len(content)} bytes) exceeds the maximum allowed limit of {max_mb} MB.",
                status_code=413,
            )

        return clean_name

    @classmethod
    def parse_file_to_dicts(cls, filename: str, content: bytes) -> List[Dict[str, Any]]:
        """Parse raw content into a list of row dictionaries."""
        ext = Path(filename).suffix.lower()

        if ext == ".csv":
            # Attempt UTF-8 with fallbacks
            for encoding in ("utf-8-sig", "utf-8", "latin-1"):
                try:
                    text = content.decode(encoding)
                    reader = csv.DictReader(io.StringIO(text))
                    if not reader.fieldnames:
                        raise UploadProcessingError("CSV file contains no headers or rows.")
                    return list(reader)
                except UnicodeDecodeError:
                    continue
            raise UploadProcessingError("Failed to decode CSV file. Please ensure UTF-8 encoding.")

        elif ext in (".xlsx", ".xls"):
            try:
                df = pd.read_excel(io.BytesIO(content), engine="openpyxl" if ext == ".xlsx" else None)
                if df.empty:
                    raise UploadProcessingError("Excel sheet is empty.")
                # Convert NaNs to None
                return df.where(pd.notnull(df), None).to_dict(orient="records")
            except Exception as e:
                logger.exception("Excel parsing failed: %s", e)
                raise UploadProcessingError(f"Failed to parse Excel file: {str(e)}")

        raise UploadProcessingError(f"Unsupported format: {ext}")

    @classmethod
    def process_and_validate(
        cls,
        upload_id: str,
        filename: str,
        content: bytes,
        max_bytes: int,
    ) -> UploadDetailResponse:
        """Complete workflow: validation, parsing, statistical aggregation, and preview generation."""
        sanitized_filename = cls.validate_file_metadata(filename, content, max_bytes)
        raw_rows = cls.parse_file_to_dicts(sanitized_filename, content)

        if not raw_rows:
            raise UploadProcessingError("The uploaded dataset contains zero data rows.")

        # Header normalization
        first_row = raw_rows[0]
        header_map: Dict[str, str] = {}
        for raw_col in first_row.keys():
            normalized = normalize_header(str(raw_col))
            if normalized:
                header_map[raw_col] = normalized

        # Check required columns
        normalized_cols = set(header_map.values())
        required_cols = {"date", "revenue", "operating_expenses"}
        missing_cols = required_cols - normalized_cols
        if missing_cols:
            raise UploadProcessingError(
                f"Missing required columns: {sorted(list(missing_cols))}. "
                "The file must include at least: date (or month/period), revenue (or sales), and operating_expenses (or expenses)."
            )

        # Row validation
        errors: List[UploadRowError] = []
        valid_records: List[Dict[str, Any]] = []
        preview_records: List[Dict[str, Any]] = []
        seen_dates: Set[str] = set()

        for idx, row in enumerate(raw_rows, start=2):  # Row 2 is first data row in spreadsheet
            row_has_error = False
            normalized_row: Dict[str, Any] = {}

            # 1. Date Validation
            raw_date = None
            for raw_key, norm_key in header_map.items():
                if norm_key == "date":
                    raw_date = row.get(raw_key)
                    break

            parsed_date = parse_date_value(raw_date)
            if not parsed_date:
                errors.append(
                    UploadRowError(
                        row=idx,
                        column="date",
                        message=f"Invalid or missing date '{raw_date}'. Expected format YYYY-MM or YYYY-MM-DD.",
                    )
                )
                row_has_error = True
            else:
                if parsed_date in seen_dates:
                    errors.append(
                        UploadRowError(
                            row=idx,
                            column="date",
                            message=f"Duplicate period '{parsed_date}'. Each reporting period must appear only once.",
                        )
                    )
                    row_has_error = True
                else:
                    seen_dates.add(parsed_date)
                    normalized_row["date"] = parsed_date

            # 2. Revenue Validation
            raw_rev = None
            for raw_key, norm_key in header_map.items():
                if norm_key == "revenue":
                    raw_rev = row.get(raw_key)
                    break

            try:
                if raw_rev is None or str(raw_rev).strip() == "":
                    raise ValueError("Revenue is required and cannot be blank.")
                rev_val = float(raw_rev)
                if rev_val < 0.0:
                    errors.append(
                        UploadRowError(
                            row=idx,
                            column="revenue",
                            message=f"Revenue cannot be negative (got {rev_val}).",
                        )
                    )
                    row_has_error = True
                else:
                    normalized_row["revenue"] = rev_val
            except (ValueError, TypeError) as e:
                errors.append(
                    UploadRowError(
                        row=idx,
                        column="revenue",
                        message=f"Invalid revenue value '{raw_rev}': must be a valid non-negative number.",
                    )
                )
                row_has_error = True

            # 3. Operating Expenses Validation
            raw_exp = None
            for raw_key, norm_key in header_map.items():
                if norm_key == "operating_expenses":
                    raw_exp = row.get(raw_key)
                    break

            try:
                if raw_exp is None or str(raw_exp).strip() == "":
                    raise ValueError("Operating expenses is required and cannot be blank.")
                exp_val = float(raw_exp)
                if exp_val < 0.0:
                    errors.append(
                        UploadRowError(
                            row=idx,
                            column="operating_expenses",
                            message=f"Operating expenses cannot be negative (got {exp_val}).",
                        )
                    )
                    row_has_error = True
                else:
                    normalized_row["operating_expenses"] = exp_val
            except (ValueError, TypeError) as e:
                errors.append(
                    UploadRowError(
                        row=idx,
                        column="operating_expenses",
                        message=f"Invalid operating expenses value '{raw_exp}': must be a valid non-negative number.",
                    )
                )
                row_has_error = True

            # 4. Optional Customers Validation
            raw_cust = None
            for raw_key, norm_key in header_map.items():
                if norm_key == "customers":
                    raw_cust = row.get(raw_key)
                    break

            if raw_cust is not None and str(raw_cust).strip() != "":
                try:
                    cust_val = int(float(raw_cust))
                    if cust_val < 0:
                        errors.append(
                            UploadRowError(row=idx, column="customers", message="Customers cannot be negative.")
                        )
                        row_has_error = True
                    else:
                        normalized_row["customers"] = cust_val
                except (ValueError, TypeError):
                    errors.append(
                        UploadRowError(row=idx, column="customers", message=f"Invalid customer count '{raw_cust}'.")
                    )
                    row_has_error = True
            else:
                normalized_row["customers"] = None

            # 5. Optional COGS Validation
            raw_cogs = None
            for raw_key, norm_key in header_map.items():
                if norm_key == "cogs":
                    raw_cogs = row.get(raw_key)
                    break

            if raw_cogs is not None and str(raw_cogs).strip() != "":
                try:
                    cogs_val = float(raw_cogs)
                    if cogs_val < 0.0:
                        errors.append(
                            UploadRowError(row=idx, column="cogs", message="COGS cannot be negative.")
                        )
                        row_has_error = True
                    else:
                        normalized_row["cogs"] = cogs_val
                except (ValueError, TypeError):
                    errors.append(
                        UploadRowError(row=idx, column="cogs", message=f"Invalid COGS value '{raw_cogs}'.")
                    )
                    row_has_error = True
            else:
                normalized_row["cogs"] = None

            # Store preview for first 10 rows
            if len(preview_records) < 10:
                preview_item = {
                    "row": idx,
                    "date": parsed_date or str(raw_date),
                    "revenue": normalized_row.get("revenue"),
                    "operating_expenses": normalized_row.get("operating_expenses"),
                    "customers": normalized_row.get("customers"),
                    "cogs": normalized_row.get("cogs"),
                    "has_error": row_has_error,
                }
                preview_records.append(preview_item)

            if not row_has_error:
                valid_records.append(normalized_row)

        total_rows = len(raw_rows)
        valid_rows = len(valid_records)
        invalid_rows = total_rows - valid_rows

        # Calculate metrics
        date_start = None
        date_end = None
        total_revenue = None
        avg_revenue = None

        if valid_records:
            sorted_by_date = sorted(valid_records, key=lambda x: x["date"])
            date_start = sorted_by_date[0]["date"]
            date_end = sorted_by_date[-1]["date"]
            total_revenue = round(sum(r["revenue"] for r in valid_records), 2)
            avg_revenue = round(total_revenue / len(valid_records), 2)

        # Determine overall status
        if invalid_rows == 0:
            status = UploadStatus.VALID
            message = f"All {valid_rows} historical records validated successfully."
        elif valid_rows > 0:
            status = UploadStatus.WARNING
            message = (
                f"Dataset contains {valid_rows} valid records and {invalid_rows} invalid rows. "
                "Resolve errors before using in analyses for maximum confidence."
            )
        else:
            status = UploadStatus.INVALID
            message = f"All {total_rows} data rows failed validation. Please inspect error details."

        summary = UploadSummaryMetrics(
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            date_start=date_start,
            date_end=date_end,
            total_revenue=total_revenue,
            average_monthly_revenue=avg_revenue,
            currency="INR",
        )

        return UploadDetailResponse(
            upload_id=upload_id,
            filename=sanitized_filename,
            file_size_bytes=len(content),
            status=status,
            summary=summary,
            errors=errors,
            preview=preview_records,
            message=message,
            created_at=datetime.now(),
        )
