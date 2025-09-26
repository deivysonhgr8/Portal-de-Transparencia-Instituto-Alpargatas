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
text = '''Municípios com maiores Índices de Qualidade da Educação (I,Q,E):

Cabaceiras (I,Q,E: 10 ponto 00)
Localizada no semiárido paraibano, Cabaceiras é conhecida como a 'Roliúde Nordestina' por ser cenário de muitos filmes nacionais. A cidade 
enfrenta os desafios do clima seco, mas possui uma forte identidade cultural.

Queimadas (I,Q,E: 9 ponto 27)
Integrando a região metropolitana de Campina Grande, Queimadas é um município com forte atividade industrial e comercial, o que reflete em uma dinâmica 
socioeconômica mais robusta em comparação com cidades do interior.

Montes Claros (I,Q,E: 7 ponto 85)
Principal centro urbano do norte de Minas Gerais, Montes Claros é um polo de serviços, educação e saúde para uma vasta região. Enfrenta os desafios 
de uma cidade de grande porte, com diversidade socioeconômica.
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
    sf.write('destaques.wav', audio_completo, 24000)
    print(f"Arquivo salvo: destaques.wav")

lang_code = 'p'

pipeline = KPipeline(lang_code=lang_code)
text = '''Municípios que representam pontos de atenção máxima (I,Q,E mais baixos):

Itatuba (I,Q,E: 1ponto 00)
A nota mínima de 1 ponto 0 no I,Q,E sinaliza um cenário de emergência educacional. Este é um ponto de atenção máximo, que exige apoio intensivo e urgente do Instituto 
para garantir o direito à educação de qualidade no município.

Santa Rita (I,Q,E: 1 ponto 69)
O I,Q,E de 1 ponto 69 é um ponto de atenção extremamente crítico. O resultado mostra que, apesar da importância econômica da cidade, a educação precisa de apoio 
estratégico para que possa evoluir e gerar oportunidades para todos.

Serra Redonda (I,Q,E: 1 ponto 83)
Um I,Q,E de 1 ponto 83 representa um ponto de atenção máximo. Este valor indica a necessidade de um plano de ação focado e urgente do Instituto para apoiar o 
município a construir uma base sólida para a educação.
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
    sf.write('pontos_críticos.wav', audio_criticos, 24000)
    print(f"Arquivo salvo: pontos_críticos.wav")