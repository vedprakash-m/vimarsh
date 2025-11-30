"""
Voice Configuration for Azure Speech Services
Maps 25 personalities to gender-appropriate Azure Neural Voices with SSML settings.

Each personality has:
- voice_name: Azure Neural Voice identifier
- gender: male/female
- locale: en-IN, en-US, en-GB, it-IT
- style: SSML express-as style (empathetic, calm, cheerful, etc.)
- rate: Speaking rate (0.5-2.0, default 1.0)
- pitch: Pitch adjustment (-50% to +50%)
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class VoiceConfig:
    """Configuration for a personality's voice settings."""
    voice_name: str
    gender: str
    locale: str
    style: str
    rate: str
    pitch: str
    description: str


# Azure Neural Voice Configuration for 25 Personalities
PERSONALITY_VOICE_CONFIG: Dict[str, VoiceConfig] = {
    # ═══════════════════════════════════════════════════════════════
    # 🕉️ SPIRITUAL DOMAIN - Calm, Empathetic, Contemplative Voices
    # ═══════════════════════════════════════════════════════════════
    
    "krishna": VoiceConfig(
        voice_name="en-IN-PrabhatNeural",
        gender="male",
        locale="en-IN",
        style="empathetic",
        rate="0.85",
        pitch="-5%",
        description="Divine guide with calm, empathetic Indian English voice"
    ),
    
    "buddha": VoiceConfig(
        voice_name="en-IN-PrabhatNeural",
        gender="male",
        locale="en-IN",
        style="calm",
        rate="0.80",
        pitch="-8%",
        description="Enlightened teacher with serene, measured Indian English voice"
    ),
    
    "jesus": VoiceConfig(
        voice_name="en-US-DavisNeural",
        gender="male",
        locale="en-US",
        style="gentle",
        rate="0.85",
        pitch="0%",
        description="Compassionate teacher with gentle, warm American voice"
    ),
    
    "jesus_christ": VoiceConfig(
        voice_name="en-US-DavisNeural",
        gender="male",
        locale="en-US",
        style="gentle",
        rate="0.85",
        pitch="0%",
        description="Compassionate teacher with gentle, warm American voice"
    ),
    
    "rumi": VoiceConfig(
        voice_name="en-GB-RyanNeural",
        gender="male",
        locale="en-GB",
        style="lyrical",
        rate="0.90",
        pitch="+2%",
        description="Mystical poet with lyrical, expressive British voice"
    ),
    
    "swami_vivekananda": VoiceConfig(
        voice_name="en-IN-PrabhatNeural",
        gender="male",
        locale="en-IN",
        style="cheerful",
        rate="0.95",
        pitch="+5%",
        description="Inspiring spiritual leader with energetic Indian English voice"
    ),
    
    "vivekananda": VoiceConfig(
        voice_name="en-IN-PrabhatNeural",
        gender="male",
        locale="en-IN",
        style="cheerful",
        rate="0.95",
        pitch="+5%",
        description="Inspiring spiritual leader with energetic Indian English voice"
    ),
    
    # ═══════════════════════════════════════════════════════════════
    # 🔬 SCIENTIFIC DOMAIN - Clear, Intellectual, Articulate Voices
    # ═══════════════════════════════════════════════════════════════
    
    "einstein": VoiceConfig(
        voice_name="en-US-GuyNeural",
        gender="male",
        locale="en-US",
        style="friendly",
        rate="0.90",
        pitch="0%",
        description="Brilliant scientist with friendly, approachable American voice"
    ),
    
    "albert_einstein": VoiceConfig(
        voice_name="en-US-GuyNeural",
        gender="male",
        locale="en-US",
        style="friendly",
        rate="0.90",
        pitch="0%",
        description="Brilliant scientist with friendly, approachable American voice"
    ),
    
    "newton": VoiceConfig(
        voice_name="en-GB-RyanNeural",
        gender="male",
        locale="en-GB",
        style="serious",
        rate="0.85",
        pitch="-3%",
        description="Mathematical genius with scholarly, precise British voice"
    ),
    
    "isaac_newton": VoiceConfig(
        voice_name="en-GB-RyanNeural",
        gender="male",
        locale="en-GB",
        style="serious",
        rate="0.85",
        pitch="-3%",
        description="Mathematical genius with scholarly, precise British voice"
    ),
    
    "tesla": VoiceConfig(
        voice_name="en-US-DavisNeural",
        gender="male",
        locale="en-US",
        style="excited",
        rate="0.95",
        pitch="+3%",
        description="Visionary inventor with enthusiastic, energetic voice"
    ),
    
    "nikola_tesla": VoiceConfig(
        voice_name="en-US-DavisNeural",
        gender="male",
        locale="en-US",
        style="excited",
        rate="0.95",
        pitch="+3%",
        description="Visionary inventor with enthusiastic, energetic voice"
    ),
    
    "archimedes": VoiceConfig(
        voice_name="en-GB-ThomasNeural",
        gender="male",
        locale="en-GB",
        style="newscast",
        rate="0.88",
        pitch="-2%",
        description="Ancient mathematician with authoritative, classic voice"
    ),
    
    "leonardo_da_vinci": VoiceConfig(
        voice_name="it-IT-DiegoNeural",
        gender="male",
        locale="it-IT",
        style="chat",
        rate="0.90",
        pitch="0%",
        description="Renaissance polymath with creative, Italian-accented voice"
    ),
    
    "da_vinci": VoiceConfig(
        voice_name="it-IT-DiegoNeural",
        gender="male",
        locale="it-IT",
        style="chat",
        rate="0.90",
        pitch="0%",
        description="Renaissance polymath with creative, Italian-accented voice"
    ),
    
    # ═══════════════════════════════════════════════════════════════
    # 🏛️ LEADERSHIP DOMAIN - Authoritative, Inspiring, Dignified Voices
    # ═══════════════════════════════════════════════════════════════
    
    "lincoln": VoiceConfig(
        voice_name="en-US-GuyNeural",
        gender="male",
        locale="en-US",
        style="hopeful",
        rate="0.85",
        pitch="-5%",
        description="Great emancipator with dignified, hopeful American voice"
    ),
    
    "abraham_lincoln": VoiceConfig(
        voice_name="en-US-GuyNeural",
        gender="male",
        locale="en-US",
        style="hopeful",
        rate="0.85",
        pitch="-5%",
        description="Great emancipator with dignified, hopeful American voice"
    ),
    
    "gandhi": VoiceConfig(
        voice_name="en-IN-PrabhatNeural",
        gender="male",
        locale="en-IN",
        style="calm",
        rate="0.80",
        pitch="-3%",
        description="Father of the nation with peaceful, determined Indian English voice"
    ),
    
    "mahatma_gandhi": VoiceConfig(
        voice_name="en-IN-PrabhatNeural",
        gender="male",
        locale="en-IN",
        style="calm",
        rate="0.80",
        pitch="-3%",
        description="Father of the nation with peaceful, determined Indian English voice"
    ),
    
    "martin_luther_king_jr": VoiceConfig(
        voice_name="en-US-GuyNeural",
        gender="male",
        locale="en-US",
        style="hopeful",
        rate="0.90",
        pitch="+5%",
        description="Civil rights leader with inspiring, passionate American voice"
    ),
    
    "mlk": VoiceConfig(
        voice_name="en-US-GuyNeural",
        gender="male",
        locale="en-US",
        style="hopeful",
        rate="0.90",
        pitch="+5%",
        description="Civil rights leader with inspiring, passionate American voice"
    ),
    
    "george_washington": VoiceConfig(
        voice_name="en-US-DavisNeural",
        gender="male",
        locale="en-US",
        style="serious",
        rate="0.85",
        pitch="-5%",
        description="Founding father with dignified, authoritative American voice"
    ),
    
    "washington": VoiceConfig(
        voice_name="en-US-DavisNeural",
        gender="male",
        locale="en-US",
        style="serious",
        rate="0.85",
        pitch="-5%",
        description="Founding father with dignified, authoritative American voice"
    ),
    
    "benjamin_franklin": VoiceConfig(
        voice_name="en-US-GuyNeural",
        gender="male",
        locale="en-US",
        style="friendly",
        rate="0.90",
        pitch="0%",
        description="Polymath statesman with witty, wise American voice"
    ),
    
    "franklin": VoiceConfig(
        voice_name="en-US-GuyNeural",
        gender="male",
        locale="en-US",
        style="friendly",
        rate="0.90",
        pitch="0%",
        description="Polymath statesman with witty, wise American voice"
    ),
    
    "chanakya": VoiceConfig(
        voice_name="en-IN-PrabhatNeural",
        gender="male",
        locale="en-IN",
        style="serious",
        rate="0.88",
        pitch="-3%",
        description="Ancient strategist with calculated, wise Indian English voice"
    ),
    
    # ═══════════════════════════════════════════════════════════════
    # 💭 PHILOSOPHICAL DOMAIN - Contemplative, Measured, Wise Voices
    # ═══════════════════════════════════════════════════════════════
    
    "marcus_aurelius": VoiceConfig(
        voice_name="en-GB-RyanNeural",
        gender="male",
        locale="en-GB",
        style="calm",
        rate="0.85",
        pitch="-5%",
        description="Stoic emperor with measured, contemplative British voice"
    ),
    
    "aurelius": VoiceConfig(
        voice_name="en-GB-RyanNeural",
        gender="male",
        locale="en-GB",
        style="calm",
        rate="0.85",
        pitch="-5%",
        description="Stoic emperor with measured, contemplative British voice"
    ),
    
    "socrates": VoiceConfig(
        voice_name="en-GB-ThomasNeural",
        gender="male",
        locale="en-GB",
        style="chat",
        rate="0.88",
        pitch="0%",
        description="Questioning philosopher with inquisitive, engaging British voice"
    ),
    
    "plato": VoiceConfig(
        voice_name="en-GB-RyanNeural",
        gender="male",
        locale="en-GB",
        style="calm",
        rate="0.85",
        pitch="-3%",
        description="Idealist philosopher with thoughtful, academic British voice"
    ),
    
    "aristotle": VoiceConfig(
        voice_name="en-GB-ThomasNeural",
        gender="male",
        locale="en-GB",
        style="newscast",
        rate="0.88",
        pitch="-2%",
        description="Systematic philosopher with authoritative, scholarly British voice"
    ),
    
    "confucius": VoiceConfig(
        voice_name="en-US-GuyNeural",
        gender="male",
        locale="en-US",
        style="calm",
        rate="0.82",
        pitch="-5%",
        description="Chinese sage with wise, patient American voice"
    ),
    
    "lao_tzu": VoiceConfig(
        voice_name="en-US-DavisNeural",
        gender="male",
        locale="en-US",
        style="calm",
        rate="0.78",
        pitch="-8%",
        description="Taoist master with serene, unhurried American voice"
    ),
    
    "laotzu": VoiceConfig(
        voice_name="en-US-DavisNeural",
        gender="male",
        locale="en-US",
        style="calm",
        rate="0.78",
        pitch="-8%",
        description="Taoist master with serene, unhurried American voice"
    ),
    
    # ═══════════════════════════════════════════════════════════════
    # 📚 LITERARY DOMAIN - Expressive, Theatrical, Lyrical Voices
    # ═══════════════════════════════════════════════════════════════
    
    "shakespeare": VoiceConfig(
        voice_name="en-GB-RyanNeural",
        gender="male",
        locale="en-GB",
        style="cheerful",
        rate="0.88",
        pitch="+3%",
        description="Bard of Avon with theatrical, expressive British voice"
    ),
    
    "william_shakespeare": VoiceConfig(
        voice_name="en-GB-RyanNeural",
        gender="male",
        locale="en-GB",
        style="cheerful",
        rate="0.88",
        pitch="+3%",
        description="Bard of Avon with theatrical, expressive British voice"
    ),
    
    "tagore": VoiceConfig(
        voice_name="en-IN-PrabhatNeural",
        gender="male",
        locale="en-IN",
        style="lyrical",
        rate="0.85",
        pitch="0%",
        description="Nobel laureate poet with lyrical, melodic Indian English voice"
    ),
    
    "rabindranath_tagore": VoiceConfig(
        voice_name="en-IN-PrabhatNeural",
        gender="male",
        locale="en-IN",
        style="lyrical",
        rate="0.85",
        pitch="0%",
        description="Nobel laureate poet with lyrical, melodic Indian English voice"
    ),
    
    # ═══════════════════════════════════════════════════════════════
    # 🧠 PSYCHOLOGY DOMAIN - Analytical, Clinical, Thoughtful Voice
    # ═══════════════════════════════════════════════════════════════
    
    "freud": VoiceConfig(
        voice_name="en-GB-ThomasNeural",
        gender="male",
        locale="en-GB",
        style="calm",
        rate="0.88",
        pitch="-3%",
        description="Father of psychoanalysis with analytical, clinical British voice"
    ),
    
    "sigmund_freud": VoiceConfig(
        voice_name="en-GB-ThomasNeural",
        gender="male",
        locale="en-GB",
        style="calm",
        rate="0.88",
        pitch="-3%",
        description="Father of psychoanalysis with analytical, clinical British voice"
    ),
}

# Default voice for unknown personalities
DEFAULT_VOICE_CONFIG = VoiceConfig(
    voice_name="en-US-GuyNeural",
    gender="male",
    locale="en-US",
    style="friendly",
    rate="0.90",
    pitch="0%",
    description="Default friendly male voice"
)


def get_voice_config(personality: str) -> VoiceConfig:
    """
    Get voice configuration for a personality.
    
    Args:
        personality: Personality name (case-insensitive, spaces converted to underscores)
        
    Returns:
        VoiceConfig for the personality, or default if not found
    """
    # Normalize personality name
    normalized = personality.lower().strip().replace(" ", "_").replace("-", "_")
    
    return PERSONALITY_VOICE_CONFIG.get(normalized, DEFAULT_VOICE_CONFIG)


def get_all_voice_configs() -> Dict[str, VoiceConfig]:
    """Return all personality voice configurations."""
    return PERSONALITY_VOICE_CONFIG.copy()


def get_voices_by_locale(locale: str) -> Dict[str, VoiceConfig]:
    """Get all voice configurations for a specific locale."""
    return {
        name: config 
        for name, config in PERSONALITY_VOICE_CONFIG.items() 
        if config.locale == locale
    }


def get_voices_by_style(style: str) -> Dict[str, VoiceConfig]:
    """Get all voice configurations for a specific style."""
    return {
        name: config 
        for name, config in PERSONALITY_VOICE_CONFIG.items() 
        if config.style == style
    }
