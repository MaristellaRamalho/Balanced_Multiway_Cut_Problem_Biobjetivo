# Bi-Objective Balanced Multiway Cut Problem (BOBMCP)

Na entrada do BOBMCP temos um grafo não direcionado $G = (V,E)$, com custos $c_e \geq 0$ nas arestas, e $K$ vértices distintos $s_1, \dots, s_K \in V$, chamados terminais. Objetiva-se remover um conjunto $F$ de arestas com menor custo de maneira que nenhum par de vértices $s_i$ e $s_j$, para $i \neq j$, esteja no mesmo componente conexo de $G' = (V, E \backslash F)$ e de forma que o tamanho da maior componente seja minimizado, buscando soluções balanceadas.

---

## Para trabalhos futuros:
* As pastas ```pareto``` e ```statistics``` guardam os resultados reportados no artigo SBPO 2026, que foram gerados considerando : ```nsbrkgaColoracaoMax```, ```nsbrkgaColoracaoQuad```, ```nsbrkgaKruskalMax```, ```nsbrkgaKruskalQuad``` e também o método exato (```CPLEX```);
* Os solvers ```nsbrkgaColoracaoBaseMax``` e ```nsbrkgaColoracaoBaseQuad``` foram implementados considerando uma versão mais simples do decoder de coloração que apenas faz a atribuição de cores e considera que um nó faz parte da componente de um terminal se tiver a mesma cor que o terminal. Isso foi feito para permitir soluções que possuem componentes não conexas, na esperança de melhorar o balanceamento. Considerações:
    * Os solvers ```nsbrkgaColoracaoBaseMax``` e ```nsbrkgaColoracaoBaseQuad``` funcionam corretamente com a busca local desligada e são os únicos decoders adaptados no código para funcionar com busca local. A busca local pode ser configurada no arquivo ```nsbrkga_solver.hpp``` referente a cada solver, atraves dos parâmetros ```std::string local_search_type = "switchSingleNodeColor"; e unsigned max_local_search_iterations (0 desliga a busca);```. Estes parâmetros tambem podem ser passados pela linha de comando;
    * A única busca local desenvolvida até aqui é ```switchSingleNodeColor``` responsável por mudar a cor de um nó em uma componente maior para a cor de um nó em uma componente menor, se isto não piorar o custo do corte. Entretanto, A BUSCA LOCAL NÃO FUNCIONA CORRETAMENTE NO PROCESSO EVOLUTIVO, POIS RETORNA SOLUÇÕES DOMINADAS;
    * A ideia central implementada parece correta quando testada fora do processo evolutivo, mas a BUSCA LOCAL PRECISA SER REATORADA;
