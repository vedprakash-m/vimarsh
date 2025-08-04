#!/usr/bin/env python3
"""
Quick Personality Content Generator

Since we need the personality content locally and you have the data in production,
this script creates basic content files for each personality to get the system
working immediately. You can replace with production data later.
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def create_basic_personality_content():
    """Create basic content files for all personalities"""
    
    # Define the output directory
    sources_dir = Path(__file__).parent.parent / "data" / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    
    # Define basic content for each personality (just to get started)
    personality_content = {
        "buddha": [
            {
                "text": "All conditioned things are impermanent. Work out your salvation with diligence.",
                "source": "Buddha's Last Words",
                "title": "Final Teaching",
                "metadata": {"type": "core_teaching"}
            },
            {
                "text": "The mind is everything. What you think you become.",
                "source": "Dhammapada",
                "title": "Mind Teaching", 
                "metadata": {"type": "wisdom"}
            },
            {
                "text": "Peace comes from within. Do not seek it without.",
                "source": "Buddhist Teaching",
                "title": "Inner Peace",
                "metadata": {"type": "meditation"}
            }
        ],
        "jesus": [
            {
                "text": "Love your enemies and pray for those who persecute you.",
                "source": "Matthew 5:44",
                "title": "Love of Enemies",
                "metadata": {"type": "core_teaching"}
            },
            {
                "text": "I am the way and the truth and the life.",
                "source": "John 14:6", 
                "title": "The Way",
                "metadata": {"type": "identity"}
            },
            {
                "text": "Peace I leave with you; my peace I give you.",
                "source": "John 14:27",
                "title": "Gift of Peace",
                "metadata": {"type": "promise"}
            }
        ],
        "einstein": [
            {
                "text": "Imagination is more important than knowledge. Knowledge is limited; imagination embraces the entire world.",
                "source": "Einstein Interview",
                "title": "Power of Imagination",
                "metadata": {"type": "philosophy"}
            },
            {
                "text": "Try not to become a person of success, but rather try to become a person of value.",
                "source": "Einstein Quote",
                "title": "Value vs Success",
                "metadata": {"type": "life_advice"}
            },
            {
                "text": "The important thing is not to stop questioning. Curiosity has its own reason for existing.",
                "source": "Einstein Quote",
                "title": "Curiosity",
                "metadata": {"type": "learning"}
            }
        ],
        "lincoln": [
            {
                "text": "A house divided against itself cannot stand.",
                "source": "Lincoln Speech 1858",
                "title": "House Divided",
                "metadata": {"type": "political_wisdom"}
            },
            {
                "text": "Nearly all men can stand adversity, but if you want to test a man's character, give him power.",
                "source": "Lincoln Quote",
                "title": "Character Test",
                "metadata": {"type": "leadership"}
            },
            {
                "text": "Government of the people, by the people, for the people, shall not perish from the earth.",
                "source": "Gettysburg Address",
                "title": "Democratic Ideal",
                "metadata": {"type": "democracy"}
            }
        ],
        "marcus_aurelius": [
            {
                "text": "You have power over your mind - not outside events. Realize this, and you will find strength.",
                "source": "Meditations",
                "title": "Mental Control",
                "metadata": {"type": "stoic_wisdom"}
            },
            {
                "text": "The best revenge is not to be like your enemy.",
                "source": "Meditations",
                "title": "Noble Response",
                "metadata": {"type": "ethics"}
            },
            {
                "text": "When you wake up in the morning, tell yourself: The people I deal with today will be meddling, ungrateful, arrogant, dishonest, jealous, and surly.",
                "source": "Meditations",
                "title": "Daily Preparation",
                "metadata": {"type": "daily_practice"}
            }
        ],
        "lao_tzu": [
            {
                "text": "The journey of a thousand miles begins with one step.",
                "source": "Tao Te Ching",
                "title": "Beginning",
                "metadata": {"type": "wisdom"}
            },
            {
                "text": "When I let go of what I am, I become what I might be.",
                "source": "Tao Te Ching", 
                "title": "Letting Go",
                "metadata": {"type": "transformation"}
            },
            {
                "text": "Nature does not hurry, yet everything is accomplished.",
                "source": "Tao Te Ching",
                "title": "Natural Timing",
                "metadata": {"type": "patience"}
            }
        ],
        "rumi": [
            {
                "text": "You were born with wings, why prefer to crawl through life?",
                "source": "Rumi Poetry",
                "title": "Born to Fly",
                "metadata": {"type": "inspiration"}
            },
            {
                "text": "The wound is the place where the Light enters you.",
                "source": "Rumi Poetry",
                "title": "Sacred Wounds",
                "metadata": {"type": "transformation"}
            },
            {
                "text": "Let yourself be silently drawn by the strange pull of what you really love. It will not lead you astray.",
                "source": "Rumi Poetry",
                "title": "Follow Love",
                "metadata": {"type": "guidance"}
            }
        ],
        "confucius": [
            {
                "text": "It does not matter how slowly you go as long as you do not stop.",
                "source": "Analects",
                "title": "Persistence",
                "metadata": {"type": "perseverance"}
            },
            {
                "text": "The man who moves a mountain begins by carrying away small stones.",
                "source": "Confucian Teaching",
                "title": "Small Steps",
                "metadata": {"type": "progress"}
            },
            {
                "text": "Choose a job you love, and you will never have to work a day in your life.",
                "source": "Confucian Wisdom",
                "title": "Work and Love",
                "metadata": {"type": "career"}
            }
        ],
        "newton": [
            {
                "text": "If I have seen further it is by standing on the shoulders of Giants.",
                "source": "Letter to Robert Hooke",
                "title": "Standing on Shoulders",
                "metadata": {"type": "humility"}
            },
            {
                "text": "I can calculate the motion of heavenly bodies, but not the madness of people.",
                "source": "Newton Quote",
                "title": "Human Complexity",
                "metadata": {"type": "observation"}
            },
            {
                "text": "Truth is ever to be found in simplicity, and not in the multiplicity and confusion of things.",
                "source": "Newton Quote", 
                "title": "Simple Truth",
                "metadata": {"type": "philosophy"}
            }
        ],
        "tesla": [
            {
                "text": "The present is theirs; the future, for which I really worked, is mine.",
                "source": "Tesla Quote",
                "title": "Future Vision",
                "metadata": {"type": "vision"}
            },
            {
                "text": "If you want to find the secrets of the universe, think in terms of energy, frequency and vibration.",
                "source": "Tesla Quote",
                "title": "Universal Secrets",
                "metadata": {"type": "science"}
            },
            {
                "text": "The progressive development of man is vitally dependent on invention.",
                "source": "Tesla Quote",
                "title": "Innovation",
                "metadata": {"type": "progress"}
            }
        ],
        "chanakya": [
            {
                "text": "A person should not be too honest. Straight trees are cut first and honest people are screwed first.",
                "source": "Chanakya Niti",
                "title": "Strategic Honesty",
                "metadata": {"type": "strategy"}
            },
            {
                "text": "Before you start some work, always ask yourself three questions - Why am I doing it, What the results might be and Will I be successful.",
                "source": "Chanakya Niti",
                "title": "Three Questions",
                "metadata": {"type": "planning"}
            },
            {
                "text": "As soon as the fear approaches near, attack and destroy it.",
                "source": "Chanakya Niti",
                "title": "Conquering Fear",
                "metadata": {"type": "courage"}
            }
        ],
        "muhammad": [
            {
                "text": "The best of people are those who benefit others.",
                "source": "Hadith",
                "title": "Serving Others",
                "metadata": {"type": "service"}
            },
            {
                "text": "Seek knowledge from the cradle to the grave.",
                "source": "Hadith",
                "title": "Lifelong Learning",
                "metadata": {"type": "education"}
            },
            {
                "text": "A kind word is a form of charity.",
                "source": "Hadith",
                "title": "Kindness",
                "metadata": {"type": "compassion"}
            }
        ]
    }
    
    created_files = []
    
    for personality, content in personality_content.items():
        filename = f"{personality}_teachings.json"
        filepath = sources_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Created {filename} with {len(content)} items")
            created_files.append(filename)
            
        except Exception as e:
            print(f"❌ Error creating {filename}: {e}")
    
    print(f"\\n🎉 Created {len(created_files)} personality content files:")
    for filename in created_files:
        filepath = sources_dir / filename
        size = filepath.stat().st_size / 1024  # KB
        print(f"  - {filename} ({size:.1f} KB)")
    
    print(f"\\n📁 Files saved to: {sources_dir}")
    print("\\n💡 These are basic content files to get your system working.")
    print("   You can replace them with production data using the download script.")

def main():
    print("🚀 Quick Personality Content Generator")
    print("=" * 50)
    print("This will create basic content files for all 12 personalities")
    print("so your backend can start working immediately.\\n")
    
    create_basic_personality_content()
    
    print("\\n✅ Done! Your backend should now work with all 12 personalities.")
    print("💡 Restart your backend to load the new content files.")

if __name__ == "__main__":
    main()
