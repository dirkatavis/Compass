import pytest
import os
from utils.data_loader import load_mvas

# Test with a valid CSV file
def test_load_mvas_valid_csv(tmp_path):
    csv_content = "MVA1\nMVA2\nMVA3"
    csv_file = tmp_path / "valid.csv"
    csv_file.write_text(csv_content)
    
    mvas = load_mvas(str(csv_file))
    assert mvas == ["MVA1", "MVA2", "MVA3"]

# Test with an empty CSV file
def test_load_mvas_empty_csv(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")
    
    mvas = load_mvas(str(csv_file))
    assert mvas == []

# Test with a CSV file containing comments and blank lines
def test_load_mvas_with_comments_and_blanks(tmp_path):
    csv_content = "# This is a comment\n\nMVA_A\n# Another comment\nMVA_B\n"
    csv_file = tmp_path / "comments_blanks.csv"
    csv_file.write_text(csv_content)
    
    mvas = load_mvas(str(csv_file))
    assert mvas == ["MVA_A", "MVA_B"]

# Test with a non-existent CSV file
def test_load_mvas_non_existent_file():
    with pytest.raises(AssertionError, match="CSV file not found"):
        load_mvas("non_existent_file.csv")

# Test with a CSV file containing leading/trailing whitespace
def test_load_mvas_with_whitespace(tmp_path):
    csv_content = "  MVA_X  \n MVA_Y \n"
    csv_file = tmp_path / "whitespace.csv"
    csv_file.write_text(csv_content)
    
    mvas = load_mvas(str(csv_file))
    assert mvas == ["MVA_X", "MVA_Y"]

# Test with a CSV file containing multiple columns, ensuring only the first is taken
def test_load_mvas_multiple_columns(tmp_path):
    csv_content = "MVA_1,extra_data_1\nMVA_2,extra_data_2"
    csv_file = tmp_path / "multiple_columns.csv"
    csv_file.write_text(csv_content)

    mvas = load_mvas(str(csv_file))
    assert mvas == ["MVA_1", "MVA_2"]
