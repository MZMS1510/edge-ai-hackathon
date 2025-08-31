# Documentação Hackaton Edge AI Qualcomm

## Nome da Solução: Pitch Pract
### Nome do grupo: Coditores
####  Integrantes: <div align="center">
  <table>
    <tr>
     <td align="center"><a href="https://www.linkedin.com/in/ana-cristina-jardim/"><sub><b>Ana Cristina</b></sub></a></td>
     <td align="center"><a href="https://www.linkedin.com/in/carlosicaro"><sub><b>Carlos Icaro</b></sub></a></td>
     <td align="center"><a href="https://www.linkedin.com/in/ifelipemartins"><sub><b>Felipe Martins</b></sub></a></td>
     <td align="center"><a href="https://www.linkedin.com/in/gustavo-martinsg"><sub><b>Gustavo Martins</b></sub></a></td>
     <td align="center"><a href="https://www.linkedin.com/in/lavinia-mendonca/"><sub><b>Lavinia Mendonça</b></sub></a></td>
     <td align="center"><a href="https://www.linkedin.com/in/marcos-vinicius-m-silva/"></a></td>
       <td align="center"><a href="https://www.linkedin.com/in/marcos-vinicius-m-silva/"><sub><b>Marcos Marcondes</b></sub></a></td>
  </table>
</div>

## Sumário
[1. Introdução](#c1)

[2. Objetivos e Justificativa](#c2)

[3. Metodologia](#c3)

[4. Desenvolvimento e Resultados](#c4)

[5. Conclusões e Recomendações](#c5)

[6. Referências](#c6)

[Anexos](#attachments)


## <a name="c1"></a>1. Introdução

&emsp;A comunicação eficaz é um dos principais desafios enfrentados por líderes, executivos e empreendedores em ambientes de alta pressão, como apresentações, pitches e reuniões estratégicas. Muitas vezes, a dificuldade em transmitir ideias com clareza, segurança e impacto pode comprometer oportunidades importantes, seja na captação de investimentos, defesa de projetos ou conquista de novos clientes. O problema central reside na ausência de ferramentas acessíveis e seguras que permitam o treinamento realista dessas habilidades, respeitando a privacidade do usuário e oferecendo feedback objetivo sobre aspectos como postura, entonação, ritmo de fala e linguagem não verbal. Neste contexto, surge a necessidade de uma ferramenta inovadora que potencialize o desenvolvimento comunicativo de forma prática, privada e eficiente.

## <a name="c2"></a>2. Objetivos e Justificativa
### 2.1 Objetivos

&emsp;O objetivo geral deste projeto é criar uma solução inovadora que permita a líderes de área, executivos e empreendedores aprimorar suas habilidades de comunicação em pitches e apresentações, oferecendo um treinamento privado, seguro e altamente interativo. Entre os objetivos específicos, fornecer feedback sobre postura, entonação, ritmo de fala e linguagem não verbal, detectar sinais de nervosismo, como tremores ou aceleração da fala; e apresentar métricas visuais de performance por meio de dashboards que auxiliem no acompanhamento do desenvolvimento são as principais propostas da aplicação. A solução se diferencia ao utilizar Edge Computing e inteligência artificial para oferecer essa análise totalmente on-device, garantindo privacidade e eliminando o julgamento humano, além de integrar funcionalidades avançadas de análise de voz e gestos, permitindo que o usuário treine de forma realista e efetiva em qualquer lugar, sem depender de instrutores presenciais ou serviços na nuvem.

### 2.2 Proposta de solução

&emsp;A solução consiste em um aplicativo desktop e mobile que roda em dispositivos equipados com Snapdragon, utilizando Edge Computing e inteligência artificial para fornecer treinamento de comunicação totalmente privado. O modelo analisa a voz, gestos e linguagem não verbal do usuário para detectar sinais de nervosismo, ritmo de fala, entonação e postura, oferecendo feedback acerca de comportamentos e métricas visuais de performance por meio de dashboards interativos. Ao combinar processamento de áudio, vídeo e capacidade para execução de LLMs diretamente no dispositivo, o modelo garante privacidade total, elimina o julgamento humano e atende aos objetivos de aprimorar a comunicação, aumentar a confiança e preparar usuários para apresentações críticas, de forma segura e prática. Por rodar localmente, a ferramenta se torna mais acessível economicamente e pode ser utilizada mesmo em locais com pouca ou nenhuma conexão de rede, garantindo que qualquer usuário tenha acesso às funcionalidades essenciais em qualquer lugar.

### 2.3 Justificativa

&emsp;A proposta se justifica pelo potencial de transformar o treinamento de comunicação em pitches e apresentações, tornando-o mais seguro, acessível e eficaz. Diferente de treinamentos tradicionais, que são caros e muitas vezes expõem o indivíduo a julgamentos e vazamento de dados, esta solução permite que líderes, executivos e empreendedores pratiquem em ambientes privados, recebendo feedback de IA sobre postura, entonação, ritmo e linguagem não verbal. Ao rodar localmente em dispositivos equipados com Snapdragon, a ferramenta garante privacidade total, reduz custos e pode ser utilizada mesmo em locais com pouca ou nenhuma conexão de rede, aumentando seu alcance. Seu diferencial está na integração entre análise de voz, gestos e simulações realistas, criando uma experiência de treinamento completa e realista que combina performance, aprendizado e segurança de forma completa e eficiente. 

## <a name="c4"></a>3. Desenvolvimento e Resultados

### 3.1.1. Planejamento Geral da Solução

a) Quais os dados disponíveis (fonte e conteúdo - exemplo: dados da área de Compras da empresa descrevendo seus fornecedores).<br>
b) Qual a solução proposta (pode ser um resumo do texto da Seção 2.2).<br>
c) Como a solução proposta deverá ser utilizada.<br>
d) Quais os benefícios trazidos pela solução proposta.<br>
e) Qual será o critério de sucesso.

### 3.1.2. Público Alvo

&emsp;A definição de público-alvo é um elemento essencial no desenvolvimento de uma solução tecnológica. Ela orienta não apenas o design da experiência do usuário, mas também a narrativa de valor do produto, os canais de distribuição e a própria viabilidade de mercado. Conhecer com clareza quem são os potenciais usuários, quais dores compartilham e de que forma sua solução se conecta a essas necessidades é o que diferencia uma ideia promissora de um produto com real aderência. No caso de uma ferramenta voltada para análise e aprimoramento da comunicação em pitches de vendas e captação, compreender os perfis que mais se beneficiam dessa proposta é fundamental para guiar tanto o desenvolvimento técnico quanto a estratégia de posicionamento.

&emsp;Quando pensamos sobre o público que melhor aproveitaria a ferramenta sendo desenvolvida, três principais grupos se destacam: líderes de área, executivos e gestores, e empreendedores. Ainda que em contextos diferentes, o problema central compartilhado pelos grupos é o mesmo: a efetividade na comunicação durante a transmissão de ideias. Todos enfrentam situações em que o peso de uma apresentação é determinante para conquistar apoio, gerar confiança ou obter recursos.

&emsp;Os líderes de área se deparam com o desafio de defender projetos estratégicos dentro de suas organizações, precisando transmitir clareza e segurança para diretoria e stakeholders internos. Já os executivos e gestores têm como prioridade a manutenção de sua credibilidade em apresentações de alto impacto, sejam relatórios de resultados, reuniões com clientes ou interações com conselhos. Por fim, os empreendedores representam o grupo com maior urgência: seu sucesso em captar investimentos depende diretamente de um pitch bem executado e da forma como sua ideia é comunicada; sua preocupação com a privacidade é ainda mais crítica, já que envolve a exposição de informações confidenciais sobre o negócio.

&emsp;Apesar das diferenças de contexto, esses três perfis convergem em três necessidades centrais: aprimorar a performance de comunicação em pitches, garantir a confidencialidade de informações estratégicas e acessar uma experiência de treinamento realista e integrada. A solução proposta se posiciona justamente na interseção dessas demandas, oferecendo privacidade, análise aprofundada da performance comunicativa e treinamento interativo orientado a cenários do mundo real.

### 3.1.3. Personas

&emsp;A construção de personas é uma etapa essencial para transformar o público-alvo em perfis concretos e representativos, permitindo compreender de forma mais detalhada as necessidades, dores e objetivos dos usuários. No contexto deste projeto, as personas ajudam a orientar o desenvolvimento da ferramenta, garantindo que as funcionalidades ofereçam valor real e resolvam questões específicas de comunicação em pitches.

&emsp;Cada persona a seguir representa um segmento distinto do público-alvo — líderes de área, executivos e gestores, e empreendedores — e permite visualizar como diferentes perfis interagem com a solução, quais são suas expectativas e como a ferramenta pode atuar como um verdadeiro aliviador de dores, ajudando-os a aprimorar a performance comunicativa, treinar em ambientes realistas e manter a privacidade de informações estratégicas.

<div style="text-align: center;">
  <img src="../assets/personas/persona1.png" alt="Persona 1"/>

  <img src="../assets/personas/persona2.png" alt="Persona 1"/>

  <img src="../assets/personas/persona3.png" alt="Persona 1"/>

</div>


### 3.1.4. User Story

&emsp;A user story é fundamental no desenvolvimento de produtos, pois transforma uma necessidade ou expectativa do usuário em um requisito claro e compreensível. Ela ajuda a equipe a entender quem é o usuário, o que ele deseja realizar e por que isso é importante, garantindo que a funcionalidade desenvolvida entregue valor real. Além disso, a user story serve como ponto de partida para discussões, refinamentos e testes, permitindo priorizar tarefas, planejar iterações e criar soluções alinhadas às demandas do público-alvo. Ao manter o foco no usuário, ela fortalece a conexão entre desenvolvimento técnico e experiência prática, tornando o produto mais efetivo e aderente às necessidades do mercado.

<div style="text-align: center;">

  <img src="../assets/personas/3w3c.png" alt="Persona 1"/>

</div>

&emsp;

&emsp;A composição de User Stories conta, ainda, com uma análise INVEST, uma metodologia utilizada para avaliar a qualidade de uma user story, garantindo que ela seja independente, negociável, valiosa, estimável, adequada ao tamanho e testável. Cada critério ajuda a tornar a história clara, focada no usuário e pronta para implementação: ser independente evita dependências desnecessárias; ser negociável mantém flexibilidade na forma de entrega; ser valiosa garante que a funcionalidade entregue benefício real; ser estimável permite planejar esforço e recursos; estar adequadamente dimensionada facilita sua conclusão em iterações curtas; e ser testável assegura que critérios de aceitação possam ser verificados. Ao aplicar o INVEST, a equipe consegue priorizar, planejar e validar histórias de forma mais eficiente, aumentando a qualidade do desenvolvimento e a aderência às necessidades do usuário.

<div style="text-align: center;">

  <img src="../assets/personas/invest.png" alt="Persona 1"/>

</div>


## <a name="c5"></a>4. Conclusões e Recomendações


&emsp;O projeto Pitch Pract demonstrou que é possível criar uma ferramenta para aprimoramento de habilidades de comunicação, utilizando inteligência artificial e Edge Computing para garantir privacidade, acessibilidade e feedback objetivo. Os principais resultados incluem o desenvolvimento de um aplicativo capaz de analisar postura, entonação, ritmo de fala e linguagem não verbal, fornecendo métricas visuais e recomendações personalizadas para o usuário. A solução se mostrou eficaz ao permitir treinamentos realistas sem dependência de instrutores presenciais ou serviços em nuvem, ampliando o acesso e reduzindo custos.


&emsp;Recomenda-se a adoção do modelo em ambientes corporativos, educacionais e para empreendedores que buscam melhorar sua performance em apresentações e pitches. É importante garantir que os usuários recebam orientações claras sobre o uso da ferramenta e sobre a interpretação dos resultados, promovendo o desenvolvimento ético e estratégico das habilidades comunicativas. 

## <a name="c6"></a>5. Referências


ALMEIDA, J. The Importance of a Business Pitch. FasterCapital, 2025. Disponível em: <https://fastercapital.com/content/The-Importance-of-a-Business-Pitch.html>. Acesso em: 31 ago. 2025.

KNOWLEDGE ACADEMY. What is Effective Communication? The Knowledge Academy, 2025. Disponível em: <https://www.theknowledgeacademy.com/blog/what-is-effective-communication/>. Acesso em: 31 ago. 2025.

NATIONAL CENTER FOR BIOTECHNOLOGY INFORMATION. Effective Communication in Building Healthy and Productive Relationships. PMC, 2025. Disponível em: <https://pmc.ncbi.nlm.nih.gov/articles/PMC2793758/>. Acesso em: 31 ago. 2025.

QUALCOMM. AI App Development. Qualcomm Documentation, 2025. Disponível em: <https://docs.qualcomm.com/bundle/publicresource/topics/80-62010-1/ai-app-development.html?product=1601111740057789>. Acesso em: 31 ago. 2025.

RESEARCHGATE. Effective Communication in Building Healthy and Productive Relationships. ResearchGate, 2025. Disponível em: <https://www.researchgate.net/publication/387724975_Effective_Communication_in_Building_Healthy_and_Productive_Relationships>. Acesso em: 31 ago. 2025.

UNIVERSITY OF CENTRAL FLORIDA. The Power of Communication. Journal of the Association for Communication Administration, 2025. Disponível em: <https://stars.library.ucf.edu/jaca/vol29/iss1/7/>. Acesso em: 31 ago. 2025.

UNIVERSITY OF QUEENSLAND. Watch 3MT. Three Minute Thesis, 2025. Disponível em: <https://threeminutethesis.uq.edu.au/watch-3mt>. Acesso em: 31 ago. 2025.

