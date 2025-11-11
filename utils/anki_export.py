"""
Anki export utilities for P.E.C.S. Learning System.

Supports two export methods:
1. AnkiConnect API - Direct push to Anki (requires AnkiConnect add-on)
2. File-based export - Generate .apkg file for manual import
"""

import json
import random
from pathlib import Path
from typing import List, Optional, Dict, Any
import urllib.request
import urllib.error
import genanki


class AnkiConnectClient:
    """
    Client for interacting with AnkiConnect API.

    AnkiConnect is an Anki add-on that provides a REST API on localhost:8765.
    Install in Anki via: Tools → Add-ons → Browse & Install → Code: 2055492159
    """

    def __init__(self, url: str = "http://localhost:8765", api_key: Optional[str] = None):
        """
        Initialize AnkiConnect client.

        Args:
            url: AnkiConnect API endpoint (default: http://localhost:8765)
            api_key: Optional API key if authentication is enabled
        """
        self.url = url
        self.api_key = api_key

    def _invoke(self, action: str, params: Optional[Dict[str, Any]] = None, version: int = 6) -> Any:
        """
        Execute an AnkiConnect action.

        Args:
            action: The API action to perform
            params: Parameters for the action
            version: API version to use (default: 6)

        Returns:
            The result from AnkiConnect

        Raises:
            Exception: If the request fails or Anki returns an error
        """
        request_data = {
            "action": action,
            "version": version,
            "params": params or {}
        }

        if self.api_key:
            request_data["key"] = self.api_key

        request_json = json.dumps(request_data).encode("utf-8")

        try:
            req = urllib.request.Request(
                self.url,
                data=request_json,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = json.loads(response.read().decode("utf-8"))

                if response_data.get("error"):
                    raise Exception(f"AnkiConnect error: {response_data['error']}")

                return response_data.get("result")

        except urllib.error.URLError as e:
            raise Exception(
                f"Failed to connect to AnkiConnect. "
                f"Make sure Anki is running with AnkiConnect add-on installed. "
                f"Error: {str(e)}"
            )

    def check_connection(self) -> bool:
        """
        Check if AnkiConnect is available and responsive.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            version = self._invoke("version")
            return version is not None
        except Exception:
            return False

    def get_deck_names(self) -> List[str]:
        """
        Get list of all deck names in Anki.

        Returns:
            List of deck names
        """
        return self._invoke("deckNames")

    def create_deck(self, deck_name: str) -> int:
        """
        Create a new deck in Anki.

        Args:
            deck_name: Name for the new deck

        Returns:
            Deck ID
        """
        return self._invoke("createDeck", {"deck": deck_name})

    def add_note(
        self,
        deck_name: str,
        front: str,
        back: str,
        tags: Optional[List[str]] = None,
        model_name: str = "Basic"
    ) -> int:
        """
        Add a note (flashcard) to Anki.

        Args:
            deck_name: Name of the deck to add the note to
            front: Front of the card (question)
            back: Back of the card (answer)
            tags: Optional list of tags
            model_name: Card template to use (default: "Basic")

        Returns:
            Note ID
        """
        note = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": {
                "Front": front,
                "Back": back
            },
            "tags": tags or []
        }

        return self._invoke("addNote", {"note": note})

    def add_notes_bulk(
        self,
        deck_name: str,
        cards: List[Dict[str, str]],
        tags: Optional[List[str]] = None,
        model_name: str = "Basic"
    ) -> List[Optional[int]]:
        """
        Add multiple notes to Anki in a single request.

        Args:
            deck_name: Name of the deck to add notes to
            cards: List of dicts with 'question' and 'answer' keys
            tags: Optional list of tags to apply to all cards
            model_name: Card template to use (default: "Basic")

        Returns:
            List of note IDs (None for failed additions)
        """
        notes = []
        for card in cards:
            note = {
                "deckName": deck_name,
                "modelName": model_name,
                "fields": {
                    "Front": card["question"],
                    "Back": card["answer"]
                },
                "tags": tags or []
            }
            notes.append(note)

        return self._invoke("addNotes", {"notes": notes})


class AnkiPackageExporter:
    """
    Exporter for creating Anki package (.apkg) files using genanki.

    Generates native Anki package files that can be double-clicked to import.
    """

    @staticmethod
    def export_to_apkg(
        cards: List[Dict[str, str]],
        output_path: Path,
        deck_name: str,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Export flashcards to Anki package (.apkg) format.

        Args:
            cards: List of dicts with 'question' and 'answer' keys
            output_path: Path where to save the .apkg file
            deck_name: Name for the Anki deck
            tags: Optional list of tags to add to all cards

        Returns:
            Number of cards exported
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a model (card template) - using a unique ID based on deck name
        model_id = random.randrange(1 << 30, 1 << 31)

        pecs_model = genanki.Model(
            model_id,
            'PECS Basic Model',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '<div style="font-size: 20px; text-align: center;">{{Question}}</div>',
                    'afmt': '{{FrontSide}}<hr id="answer"><div style="font-size: 18px; text-align: center;">{{Answer}}</div>',
                },
            ],
            css="""
                .card {
                    font-family: arial;
                    font-size: 20px;
                    text-align: center;
                    color: black;
                    background-color: white;
                }
            """
        )

        # Create deck with unique ID based on deck name hash
        deck_id = random.randrange(1 << 30, 1 << 31)
        deck = genanki.Deck(deck_id, deck_name)

        # Add cards to deck
        for card in cards:
            # Replace newlines with HTML breaks
            question = card["question"].replace("\n", "<br>")
            answer = card["answer"].replace("\n", "<br>")

            note = genanki.Note(
                model=pecs_model,
                fields=[question, answer],
                tags=tags or []
            )
            deck.add_note(note)

        # Create package and write to file
        package = genanki.Package(deck)
        package.write_to_file(str(output_path))

        return len(cards)


def export_flashcards_to_anki(
    flashcards: List[Any],
    deck_name: str,
    method: str = "api",
    output_path: Optional[Path] = None,
    tags: Optional[List[str]] = None,
    anki_url: str = "http://localhost:8765"
) -> Dict[str, Any]:
    """
    High-level function to export flashcards to Anki using specified method.

    Args:
        flashcards: List of Flashcard ORM objects with 'question' and 'answer' attributes
        deck_name: Name for the Anki deck
        method: Export method - "api" for AnkiConnect or "file" for text export
        output_path: Path for file export (required if method="file")
        tags: Optional tags to add to cards
        anki_url: AnkiConnect URL (default: http://localhost:8765)

    Returns:
        Dict with status and details:
        {
            "success": bool,
            "method": str,
            "count": int,
            "message": str,
            "file_path": Optional[str]  # For file export
        }
    """
    # Convert ORM objects to dicts
    cards = [
        {"question": card.question, "answer": card.answer}
        for card in flashcards
    ]

    if not cards:
        return {
            "success": False,
            "method": method,
            "count": 0,
            "message": "No flashcards to export"
        }

    if method == "api":
        try:
            client = AnkiConnectClient(url=anki_url)

            # Check connection
            if not client.check_connection():
                return {
                    "success": False,
                    "method": "api",
                    "count": 0,
                    "message": (
                        "Cannot connect to AnkiConnect. "
                        "Make sure Anki is running with AnkiConnect add-on installed. "
                        "Install via: Tools → Add-ons → Code: 2055492159"
                    )
                }

            # Create deck if it doesn't exist
            existing_decks = client.get_deck_names()
            if deck_name not in existing_decks:
                client.create_deck(deck_name)

            # Add cards
            note_ids = client.add_notes_bulk(deck_name, cards, tags)

            # Count successful additions
            success_count = sum(1 for note_id in note_ids if note_id is not None)
            failed_count = len(note_ids) - success_count

            message = f"Successfully added {success_count} cards to deck '{deck_name}'"
            if failed_count > 0:
                message += f" ({failed_count} failed - possibly duplicates)"

            return {
                "success": True,
                "method": "api",
                "count": success_count,
                "message": message
            }

        except Exception as e:
            return {
                "success": False,
                "method": "api",
                "count": 0,
                "message": f"Error: {str(e)}"
            }

    elif method == "file":
        if not output_path:
            return {
                "success": False,
                "method": "file",
                "count": 0,
                "message": "output_path is required for file export"
            }

        try:
            exporter = AnkiPackageExporter()
            count = exporter.export_to_apkg(cards, output_path, deck_name, tags)

            return {
                "success": True,
                "method": "file",
                "count": count,
                "message": f"Exported {count} cards to {output_path.name}",
                "file_path": str(output_path)
            }

        except Exception as e:
            return {
                "success": False,
                "method": "file",
                "count": 0,
                "message": f"Error: {str(e)}"
            }

    else:
        return {
            "success": False,
            "method": method,
            "count": 0,
            "message": f"Unknown export method: {method}. Use 'api' or 'file'"
        }
