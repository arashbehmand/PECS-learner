#!/usr/bin/env python3
"""
Test script for Anki export functionality.

This script tests both AnkiConnect API and file-based export methods.
"""

from pathlib import Path
from utils.anki_export import (
    AnkiConnectClient,
    AnkiFileExporter,
    export_flashcards_to_anki
)


class MockFlashcard:
    """Mock flashcard object for testing"""
    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer = answer


def test_ankiconnect_connection():
    """Test if AnkiConnect is available"""
    print("=" * 60)
    print("Testing AnkiConnect Connection")
    print("=" * 60)

    client = AnkiConnectClient()

    try:
        is_connected = client.check_connection()
        if is_connected:
            print("✓ AnkiConnect is running and accessible")

            # Try to get deck names
            decks = client.get_deck_names()
            print(f"✓ Found {len(decks)} existing decks:")
            for deck in decks[:5]:  # Show first 5
                print(f"  - {deck}")
            if len(decks) > 5:
                print(f"  ... and {len(decks) - 5} more")

            return True
        else:
            print("✗ AnkiConnect is not responding")
            print("\nTo use AnkiConnect:")
            print("1. Open Anki")
            print("2. Go to Tools → Add-ons → Browse & Install")
            print("3. Enter code: 2055492159")
            print("4. Restart Anki")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_file_export():
    """Test file-based export"""
    print("\n" + "=" * 60)
    print("Testing File-Based Export")
    print("=" * 60)

    # Create test flashcards
    test_cards = [
        MockFlashcard("What is Python?", "A high-level programming language"),
        MockFlashcard("What is PECS?", "Prime, Engage, Challenge, Solidify learning method"),
        MockFlashcard("What is Anki?", "A spaced repetition flashcard application"),
    ]

    output_path = Path("data/exports/test_export.txt")

    try:
        result = export_flashcards_to_anki(
            flashcards=test_cards,
            deck_name="PECS Test Deck",
            method="file",
            output_path=output_path,
            tags=["test", "pecs"]
        )

        if result["success"]:
            print(f"✓ {result['message']}")
            print(f"✓ File saved to: {result['file_path']}")

            # Verify file content
            with open(output_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                print(f"✓ File contains {len(lines)} lines")

                if lines:
                    print("\nSample content:")
                    for i, line in enumerate(lines[:2], 1):
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            print(f"  Card {i}: Q: '{parts[0][:50]}...' A: '{parts[1][:50]}...'")

            return True
        else:
            print(f"✗ Export failed: {result['message']}")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_export():
    """Test AnkiConnect API export"""
    print("\n" + "=" * 60)
    print("Testing AnkiConnect API Export")
    print("=" * 60)

    # Create test flashcards
    test_cards = [
        MockFlashcard("API Test Question 1", "API Test Answer 1"),
        MockFlashcard("API Test Question 2", "API Test Answer 2"),
    ]

    try:
        result = export_flashcards_to_anki(
            flashcards=test_cards,
            deck_name="PECS Test Deck (API)",
            method="api",
            tags=["test", "pecs", "api"]
        )

        if result["success"]:
            print(f"✓ {result['message']}")
            print("✓ Check Anki to see the new cards!")
            return True
        else:
            print(f"✗ Export failed: {result['message']}")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ANKI EXPORT FUNCTIONALITY TEST")
    print("=" * 60 + "\n")

    # Test file export (always works)
    file_success = test_file_export()

    # Test AnkiConnect connection
    anki_connected = test_ankiconnect_connection()

    # Test API export only if connected
    if anki_connected:
        api_success = test_api_export()
    else:
        api_success = False
        print("\nSkipping API export test (AnkiConnect not available)")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"File Export:      {'✓ PASSED' if file_success else '✗ FAILED'}")
    print(f"AnkiConnect:      {'✓ AVAILABLE' if anki_connected else '✗ NOT AVAILABLE'}")
    print(f"API Export:       {'✓ PASSED' if api_success else '✗ SKIPPED/FAILED'}")
    print("=" * 60)

    if file_success:
        print("\n✓ File export is working correctly!")
        print("  You can manually import the .txt file into Anki.")

    if anki_connected and api_success:
        print("\n✓ AnkiConnect API is working correctly!")
        print("  You can push cards directly to Anki from the app.")

    if not anki_connected:
        print("\nℹ To enable direct API export:")
        print("  1. Install AnkiConnect add-on (code: 2055492159)")
        print("  2. Make sure Anki is running")
        print("  3. Try running this test again")

    print("\n")


if __name__ == "__main__":
    main()
