import asyncio
from unittest.mock import patch

import pytest

from backend.spiritual_guidance.api import SpiritualGuidanceAPI


@pytest.mark.asyncio
async def test_citation_extraction_and_confidence():
    """Ensure citations are parsed from LLM output and confidence is set."""
    api = SpiritualGuidanceAPI()

    # Mock context returned by RAG
    mock_context = [
        {
            "text": "dharmād hy api parityajya māṁ ekaṁ śaraṇaṁ vraja",
            "source": "Bhagavad Gita",
            "chapter": 18,
            "verse": 66,
            "relevance_score": 0.95,
        },
        {
            "text": "karmaṇy-evādhikāras te mā phaleṣu kadācana",
            "source": "Bhagavad Gita",
            "chapter": 2,
            "verse": 47,
            "relevance_score": 0.90,
        },
    ]

    # Response that references both chunks
    mock_llm_output = (
        "Dear devotee, surrender unto Me and I shall protect you. [[CITATION:0]] "
        "Perform your duty without attachment to results. [[CITATION:1]]"
    )

    with patch.object(api, "_retrieve_context", return_value=mock_context), \
         patch.object(api, "_call_gemini_safely", return_value=mock_llm_output):

        result = await api.process_query("What is the essence of surrender?", include_citations=True)

    citations = result["citations"]
    assert len(citations) == 2
    # Ensure confidence score averaged correctly (~0.925)
    assert abs(result["metadata"]["confidence_score"] - 0.925) < 0.01
    # Check citation fields exist
    for c in citations:
        assert "source" in c and "chapter" in c and "verse" in c 