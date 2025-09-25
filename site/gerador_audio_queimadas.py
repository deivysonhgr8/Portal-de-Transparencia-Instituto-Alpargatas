from kokoro import KPipeline
import soundfile as sf
import torch
import numpy as np

# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇪🇸 'e' => Spanish es
# 🇫🇷 'f' => French fr-fr
# 🇮🇳 'h' => Hindi hi
# 🇮🇹 'i' => Italian it
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇧🇷 'p' => Brazilian Portuguese pt-br
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]
lang_code = 'p'

pipeline = KPipeline(lang_code=lang_code)
text = '''Análise de Destaque: Queimadas. Com um impressionante IQE de 9.27, 
Queimadas se posiciona como um município de altíssimo desempenho educacional. 
Este índice reflete não apenas excelentes resultados de aprendizagem, mas também uma 
infraestrutura escolar de qualidade e bons indicadores de equidade, mostrando um sistema educacional robusto e eficaz.
'''

# fonte das vozes aqui: 
# http://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
voice = 'af_heart'
generator = pipeline(text, voice='pf_dora')

audio_chunks = []
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    audio_chunks.append(audio)

if audio_chunks:
    audio_completo = np.concatenate(audio_chunks)
    sf.write('audio_completo.wav', audio_completo, 24000)
    print(f"Arquivo salvo: audio_completo.wav")

lang_code = 'p'

pipeline = KPipeline(lang_code=lang_code)
text = '''Análise de Atenção: Pontos Críticos. Municípios como Itatuba, com IQE de 1.0, e Santa Rita, com 1.69, 
representam pontos de atenção máxima. Estes índices extremamente baixos sinalizam uma emergência educacional, 
com desafios críticos em todas as dimensões avaliadas, como infraestrutura, desempenho e equidade. Estes casos 
demandam apoio intensivo e urgente.
'''

# fonte das vozes aqui: 
# http://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
voice = 'af_heart'
generator = pipeline(text, voice='pf_dora')

audio_chunks = []
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    audio_chunks.append(audio)

if audio_chunks:
    audio_criticos = np.concatenate(audio_chunks)
    sf.write('audio_críticos.wav', audio_criticos, 24000)
    print(f"Arquivo salvo: audio_críticos.wav")