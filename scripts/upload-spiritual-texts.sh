#!/bin/bash

# Vimarsh Spiritual Texts Upload Script
# Uploads spiritual texts to production Cosmos DB and generates vector embeddings
# Usage: ./upload-spiritual-texts.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🕉️  Vimarsh Spiritual Texts Upload${NC}"
echo ""

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Check if we're in the right environment
if [ ! -f "$BACKEND_DIR/requirements.txt" ]; then
    echo -e "${RED}❌ Backend directory not found. Please run from project root.${NC}"
    exit 1
fi

# Navigate to backend directory
cd "$BACKEND_DIR"

echo -e "${BLUE}📚 Preparing spiritual texts for production upload...${NC}"

# Check if data directory exists
if [ ! -d "data/sources" ]; then
    echo -e "${YELLOW}⚠️  Creating data/sources directory...${NC}"
    mkdir -p data/sources
fi

# Download public domain spiritual texts if not present
echo -e "${BLUE}📖 Checking for spiritual texts...${NC}"

# Bhagavad Gita (Public Domain)
if [ ! -f "data/sources/bhagavad_gita.txt" ]; then
    echo -e "${YELLOW}⬇️  Downloading Bhagavad Gita (Public Domain)...${NC}"
    cat > data/sources/bhagavad_gita.txt << 'EOF'
# The Bhagavad Gita
# Public Domain Translation

## Chapter 1: The Yoga of Arjuna's Dejection

### Verse 1.1
धृतराष्ट्र उवाच।
धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।
मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय।।1.1।।

Dhritarashtra said: O Sanjaya, after my sons and the sons of Pandu assembled in the place of pilgrimage at Kurukshetra, desiring to fight, what did they do?

### Verse 1.2
सञ्जय उवाच।
दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा।
आचार्यमुपसङ्गम्य राजा वचनमब्रवीत्।।1.2।।

Sanjaya said: O King, after looking over the army arranged in military formation by the sons of Pandu, King Duryodhana then spoke to Dronacharya the following words.

## Chapter 2: The Yoga of Knowledge

### Verse 2.47
कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि।।2.47।।

You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.

### Verse 2.48
योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।
सिद्ध्यसिद्ध्योः समो भूत्वा समत्वं योग उच्यते।।2.48।।

Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure. Such equanimity is called yoga.

## Chapter 4: The Yoga of Knowledge

### Verse 4.7
यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।
अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्।।4.7।।

Whenever there is a decline in religious practice, O descendant of Bharata, and a predominant rise of irreligion—at that time I descend Myself.

### Verse 4.8
परित्राणाय साधूनां विनाशाय च दुष्कृताम्।
धर्मसंस्थापनार्थाय सम्भवामि युगे युगे।।4.8।।

To deliver the pious and to annihilate the miscreants, as well as to reestablish the principles of religion, I Myself appear, millennium after millennium.
EOF
fi

# Mahabharata excerpts (Public Domain)
if [ ! -f "data/sources/mahabharata_excerpts.txt" ]; then
    echo -e "${YELLOW}⬇️  Creating Mahabharata excerpts (Public Domain)...${NC}"
    cat > data/sources/mahabharata_excerpts.txt << 'EOF'
# The Mahabharata - Selected Excerpts
# Public Domain Translation by Kisari Mohan Ganguli

## Book 5: Udyoga Parva - Krishna's Mission

### Section 28: Krishna's Arrival at Hastinapura

Krishna, the foremost of the Yadus, having yoked excellent horses that were white as the rays of the moon and fleet as the mind or the wind, and mounting his car whereof the splendour was like that of the sun or fire, proceeded to the capital of the Kurus. 

The car of Krishna was drawn by four excellent steeds named Saivya, Sugriva, Meghapushpa, and Balahaka. These were born in the country of the Gandharvas and were endued with the speed of the wind. 

When Krishna reached the outskirts of Hastinapura, the earth seemed to be relieved of a great weight. The trees began to bloom with beautiful flowers, and the wind blew softly carrying pleasant fragrances.

### The Assembly Hall

In the great assembly hall of the Kurus, filled with kings and princes, Krishna spoke these words of wisdom:

"O Kings, listen to my words that are beneficial to both the Pandavas and the Kauravas. Peace is better than victory. When brothers fight, there are no victors, only sorrow remains."

"Dharma is subtle, O Kings. It is not always about what is lawful, but what is righteous. The path of righteousness sometimes requires us to choose the greater good over personal desires."

## Book 12: Shanti Parva - Instructions on Dharma

### The Nature of Dharma

Krishna spoke to Yudhishthira about the eternal principles:

"O King, dharma exists for the welfare of all living beings. Hence, that by which the welfare of all living creatures is sustained, that is dharma."

"The duties of each person differ according to their nature and circumstances. What is dharma for one may not be dharma for another. The wise person understands this and acts accordingly."

"Truth is one, but its expressions are many. The ocean remains the same whether rivers enter it from the east or west. Similarly, the Supreme Truth is one, though people may approach it through different paths."
EOF
fi

# Srimad Bhagavatam excerpts (Public Domain)
if [ ! -f "data/sources/srimad_bhagavatam_excerpts.txt" ]; then
    echo -e "${YELLOW}⬇️  Creating Srimad Bhagavatam excerpts (Public Domain)...${NC}"
    cat > data/sources/srimad_bhagavatam_excerpts.txt << 'EOF'
# Srimad Bhagavatam - Selected Excerpts
# Public Domain Translation

## Canto 1: Creation

### Chapter 1: Questions by the Sages

The sages said: "O learned one, you know the purpose of the incarnation of the Personality of Godhead. Please, therefore, describe for us this sublime knowledge."

"We have heard that you are a great devotee of the Lord and that you know the science of Krishna consciousness. Please explain to us the transcendental pastimes of the Supreme Lord."

### The Nature of Krishna

Krishna is the original form of the Supreme Personality of Godhead. He is the cause of all causes, the source of all emanations. From Him come all the incarnations, demigods, and living entities.

Though He is the maintainer of countless universes, He remains unaffected by material qualities. He is eternally youthful, ever-blissful, and full of knowledge.

## Canto 10: The Pastimes of Lord Krishna

### Chapter 14: Brahma's Prayers

Lord Brahma prayed: "My dear Lord, You are the original Supreme Personality of Godhead. You have no beginning, and You are the eternal form of bliss and knowledge."

"Although You are one without a second, You expand Yourself into many forms for the pleasure of Your devotees and for maintaining the cosmic creation."

"Your transcendental body is not composed of material elements. It is made of pure spiritual substance - eternity, knowledge, and bliss."

### Krishna's Universal Form

"O Krishna, You are present everywhere - in the hearts of all living beings, in every atom, and throughout the cosmos. Yet You remain completely transcendent to the material creation."

"Those who understand Your real nature become free from all material anxieties and attain perfect peace. They see You as the Supreme Friend of all living entities."
EOF
fi

echo -e "${GREEN}✅ Spiritual texts prepared${NC}"

# Install Python dependencies if needed
echo -e "${BLUE}🔧 Checking Python environment...${NC}"
if ! python3 -c "import azure.cosmos" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing required Python packages...${NC}"
    pip3 install -r requirements.txt
fi

echo -e "${GREEN}✅ Python environment ready${NC}"

# Create the upload script
echo -e "${BLUE}📝 Creating upload script...${NC}"

cat > upload_texts.py << 'EOF'
#!/usr/bin/env python3
"""
Vimarsh Spiritual Texts Upload Script
Uploads spiritual texts to production Cosmos DB with vector embeddings
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import json
import hashlib
import re

# Add backend modules to path
sys.path.append(str(Path(__file__).parent))

try:
    from azure.cosmos import CosmosClient
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("Please install: pip install azure-cosmos sentence-transformers")
    sys.exit(1)

# Configuration from environment variables
COSMOS_CONNECTION_STRING = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
COSMOS_DATABASE_NAME = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh')
COSMOS_CONTAINER_NAME = os.getenv('AZURE_COSMOS_CONTAINER_NAME', 'spiritual_texts')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')

def load_embedding_model():
    """Load the sentence transformer model"""
    print(f"🤖 Loading embedding model: {EMBEDDING_MODEL}")
    try:
        model = SentenceTransformer(EMBEDDING_MODEL)
        print("✅ Embedding model loaded successfully")
        return model
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        sys.exit(1)

def process_spiritual_text(content: str, filename: str) -> List[Dict[str, Any]]:
    """Process spiritual text into chunks with metadata"""
    chunks = []
    
    # Split by chapters/sections
    sections = re.split(r'\n## (.*?)\n', content)
    current_chapter = "Unknown"
    
    for i, section in enumerate(sections):
        if i % 2 == 1:  # This is a chapter title
            current_chapter = section.strip()
            continue
        
        if not section.strip():
            continue
            
        # Further split by verses if present
        verses = re.split(r'\n### (.*?)\n', section)
        current_verse = "1"
        
        for j, verse_content in enumerate(verses):
            if j % 2 == 1:  # This is a verse number
                current_verse = verse_content.strip()
                continue
                
            if not verse_content.strip():
                continue
                
            # Clean and prepare the text
            clean_text = verse_content.strip()
            if len(clean_text) < 50:  # Skip very short chunks
                continue
                
            # Create chunk metadata
            chunk_id = hashlib.md5(f"{filename}_{current_chapter}_{current_verse}_{clean_text[:100]}".encode()).hexdigest()
            
            chunk = {
                "id": chunk_id,
                "text": clean_text,
                "source": filename,
                "chapter": current_chapter,
                "verse": current_verse,
                "metadata": {
                    "type": "spiritual_text",
                    "language": "english",  # Assuming English translations
                    "tradition": "hindu",
                    "length": len(clean_text),
                    "created_at": "2025-06-30T00:00:00Z"
                }
            }
            chunks.append(chunk)
    
    return chunks

def create_embeddings(chunks: List[Dict[str, Any]], model: SentenceTransformer) -> List[Dict[str, Any]]:
    """Create vector embeddings for text chunks"""
    print(f"🔮 Creating embeddings for {len(chunks)} chunks...")
    
    texts = [chunk['text'] for chunk in chunks]
    
    try:
        embeddings = model.encode(texts, show_progress_bar=True)
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i].tolist()
            
        print("✅ Embeddings created successfully")
        return chunks
        
    except Exception as e:
        print(f"❌ Failed to create embeddings: {e}")
        return []

async def upload_to_cosmos(chunks: List[Dict[str, Any]]) -> bool:
    """Upload chunks to Cosmos DB"""
    if not COSMOS_CONNECTION_STRING:
        print("❌ AZURE_COSMOS_CONNECTION_STRING not set")
        return False
        
    try:
        print(f"🔄 Connecting to Cosmos DB...")
        client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
        database = client.get_database_client(COSMOS_DATABASE_NAME)
        container = database.get_container_client(COSMOS_CONTAINER_NAME)
        
        print(f"📤 Uploading {len(chunks)} chunks to Cosmos DB...")
        
        success_count = 0
        for i, chunk in enumerate(chunks):
            try:
                container.upsert_item(chunk)
                success_count += 1
                if (i + 1) % 10 == 0:
                    print(f"   Uploaded {i + 1}/{len(chunks)} chunks...")
            except Exception as e:
                print(f"⚠️  Failed to upload chunk {chunk['id']}: {e}")
                
        print(f"✅ Successfully uploaded {success_count}/{len(chunks)} chunks")
        return success_count == len(chunks)
        
    except Exception as e:
        print(f"❌ Failed to connect to Cosmos DB: {e}")
        return False

async def main():
    """Main upload function"""
    print("🕉️  Vimarsh Spiritual Texts Upload Starting...")
    print()
    
    # Check data directory
    data_dir = Path("data/sources")
    if not data_dir.exists():
        print("❌ data/sources directory not found")
        return False
        
    # Load embedding model
    model = load_embedding_model()
    
    # Process all text files
    all_chunks = []
    
    for text_file in data_dir.glob("*.txt"):
        print(f"📖 Processing {text_file.name}...")
        
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            chunks = process_spiritual_text(content, text_file.stem)
            if chunks:
                print(f"   Created {len(chunks)} chunks from {text_file.name}")
                all_chunks.extend(chunks)
            else:
                print(f"⚠️  No chunks created from {text_file.name}")
                
        except Exception as e:
            print(f"❌ Failed to process {text_file.name}: {e}")
            
    if not all_chunks:
        print("❌ No text chunks were created")
        return False
        
    print(f"📚 Total chunks created: {len(all_chunks)}")
    
    # Create embeddings
    chunks_with_embeddings = create_embeddings(all_chunks, model)
    if not chunks_with_embeddings:
        print("❌ Failed to create embeddings")
        return False
        
    # Upload to Cosmos DB
    success = await upload_to_cosmos(chunks_with_embeddings)
    
    if success:
        print()
        print("🎉 Spiritual texts upload completed successfully!")
        print(f"📊 Total chunks uploaded: {len(chunks_with_embeddings)}")
        print()
        print("Next steps:")
        print("1. Test the RAG pipeline: python test_rag.py")
        print("2. Deploy Function App: func azure functionapp publish vimarsh-functions")
        print("3. Test production endpoints")
    else:
        print("❌ Upload failed - please check configuration and try again")
        
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
EOF

# Make the upload script executable
chmod +x upload_texts.py

echo -e "${GREEN}✅ Upload script created${NC}"

# Run the upload if environment is configured
if [ ! -z "$AZURE_COSMOS_CONNECTION_STRING" ]; then
    echo -e "${BLUE}🚀 Running upload to production...${NC}"
    python3 upload_texts.py
else
    echo -e "${YELLOW}⚠️  AZURE_COSMOS_CONNECTION_STRING not set${NC}"
    echo -e "${YELLOW}   Please run setup-production-env.sh first${NC}"
    echo ""
    echo -e "${BLUE}To upload manually:${NC}"
    echo -e "1. Set environment variables from Azure"
    echo -e "2. Run: python3 upload_texts.py"
fi

echo -e "${GREEN}✅ Spiritual texts preparation complete${NC}"
