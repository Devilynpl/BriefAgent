BriefAgent: Deterministyczny Agent Badawczy z Maszyną Stanów i Trace'amiProblem: Zwykły prompt "Zrób mi research o firmie X" generuje ogólniki z halucynacjami, zmyśla liczby zatrudnienia, nie potrafi zweryfikować aktualności danych i wiesza się na pierwszym błędzie sieciowym.Cel: Zbudować autonomicznego, odpornego na awarie agenta opartego o graf stanów (State Graph), który pobiera dane z zewnętrznych API/scrapingu, weryfikuje fakty, obsługuje awarie narzędzi (tool retries) i generuje ustrukturyzowany dossier biznesowy bez zmyślania.Zasada przewodnia: Workflow-First & Hard Budget — agent ma sztywne limity kroków, twardy limit kosztu, a sukces mierzymy binarną rubryką faktograficzną, a nie „ładnym stylem tekstu”.Faza 1: Definicja domeny, kontraktu stanu i rubryki sukcesu (Task Success Rubric)
W agentach brak precyzyjnego kontraktu prowadzi do zapętlenia i nieskończonych wywołań narzędzi. Zaczynamy od zdefiniowania rubryki sukcesu i centralnego stanu.
- [x] ~~**Rubryka Sukcesu Domenowego (Binary Success Rubric - 6 twardych kryteriów)**:~~
  ~~Zadanie uznaje się za zakończone sukcesem ($1$) tylko wtedy, gdy brief spełnia min. 5/6 warunków:~~
  - ~~Core Business: Precyzyjny opis czym firma zarabia (nie ogólny slogan marketingowy).~~
  - ~~Scale & Headcount: Liczba pracowników / ranga wielkości poparta źródłem.~~
  - ~~Tech Stack / Product Signals: Wskazanie technologii lub produktów z ostatnich 12 miesięcy.~~
  - ~~Pain Points / Triggers: Min. 2 realne wyzwania biznesowe (np. ekspansja, rekrutacje, zwolnienia, fuzje).~~
  - ~~Source Verification: Każdy fakt ma aktywne, zescrapowane URL (0 zmyślonych linków).~~
  - ~~Graceful Degradation: Jeśli firma jest tajnym start-upem w trybie stealth, agent wprost zaznacza brak danych zamiast halucynować.~~
- [x] ~~**Struktura Centralnego Stanu Agenta (AgentState Schema)**:~~
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

class ToolExecution(BaseModel):
    tool_name: str
    tool_input: dict
    tool_output: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float
    retry_count: int = 0

class AgentState(BaseModel):
    company_name: str
    company_domain: str
    step_count: int = 0
    max_steps: int = 12
    cost_spent_usd: float = 0.0
    cost_budget_usd: float = 0.15
    collected_evidence: Dict[str, str] = Field(default_factory=dict) # URL -> extracted text
    trace_log: List[ToolExecution] = Field(default_factory=list)
    status: Literal["PLANNING", "RESEARCHING", "VERIFYING", "SYNTHESIS", "COMPLETED", "FAILED", "UNVERIFIABLE_COMPANY"] = "PLANNING"
    final_brief: Optional[dict] = None
```
- [x] ~~**Zbiór walidacyjny (Evaluation Benchmark - 25 firm)**:~~
  - ~~10 dużych firm (dużo szumu informacyjnego, łatwo o nieaktualne dane).~~
  - ~~8 średnich software house'ów / B2B SaaS (wymagają precyzyjnego szukania).~~
  - ~~4 małe/lokalne podmioty z ubogim śladem cyfrowym.~~
  - ~~3 firmy nieistniejące / podchwytliwe (sprawdzenie natychmiastowego zgłoszenia braku danych).~~

Faza 2: Środowisko narzędziowe (Tools), Odporność (Resilience) i Mocki
Agent jest tak silny, jak jego odporność na błędy zewnętrzne (timeouty, errory 429, zablokowany scraping).
- [x] ~~**Implementacja 3 kluczowych narzędzi (Real API + Idempotent Mocki)**:~~
  - ~~`web_search(query: str, num_results: int = 5)`: Integracja z Tavily / SerpAPI z fallbackiem na lokalny mock JSON dla powtarzalnych testów CI.~~
  - ~~`scrape_page(url: str)`: Pobieranie HTML z konwersją do Markdowna (trafilatura lub cheerio-equivalent) z usuwaniem szumu (cookie banners, stopki).~~
  - ~~`domain_dns_lookup(domain: str)`: Szybka weryfikacja rekordów MX i nagłówków technicznych (czy firma w ogóle żyje).~~
- [x] ~~**Mechanizm Retry z Exponential Backoff i Circuit Breakerem**:~~
  - ~~Jeśli narzędzie zwróci błąd HTTP 429 lub 5xx, wrapper narzędzia automatycznie ponawia próbę (max 2 powtórzenia z opóźnieniem 1s $\to$ 3s).~~
  - ~~Zapisanie metryki % tool-error recovered w stanie agenta.~~
- [x] ~~**Ścisła walidacja wejść/wyjść narzędzi (Schema Guard)**:~~
  - ~~Jeśli model przekaże do narzędzia web_search błędny JSON lub URL bez protokołu, narzędzie nie rzuca nieskorelowanego wyjątku Pythonowego, lecz zwraca ustrukturyzowany błąd: `ToolError: Invalid argument 'url'. Must start with https://`, zmuszając agenta do autorefleksji.~~

Faza 3: Graf stanów (Orkiestracja), Budżetowanie i Pętla Decyzyjna
Rezygnujemy z niekontrolowanych pętli while True. Używamy deterministycznego grafu stanów (np. LangGraph lub autorskiej maszyny stanów).
- [x] ~~**Architektura Grafu Decyzyjnego**:~~
  - ~~Node: Planner: Rozbija cel na 3 konkretne hipotezy do sprawdzenia (oferta, skala, newsy).~~
  - ~~Node: Tool Caller: Wykonuje równolegle lub sekwencyjnie zaplanowane akcje.~~
  - ~~Node: Evaluator / Fact-Checker: Sprawdza, czy zebrane fakty odpowiadają na rubrykę. Jeśli nie — decyduje o kolejnym kroku badawczym.~~
  - ~~Node: Synthesizer: Buduje ostateczny raport.~~
- [x] ~~**Mechanizm twardego budżetu (Cost & Step Limiter)**:~~
  - ~~step_count >= 12 $\to$ natychmiastowe przejście do syntezy cząstkowej z ostrzeżeniem „Przekroczono limit kroków”.~~
  - ~~cost_spent_usd >= $0.15 $\to$ natychmiastowe przerwanie pętli badawczej i generacja z danych już zgromadzonych.~~
- [x] ~~**Graceful Failure Node**:~~
  - ~~Jeśli po 3 krokach agent nie znalazł żadnych rzetelnych źródeł, graf omija syntezę i kończy działanie statusem UNVERIFIABLE_COMPANY, uniemożliwiając zmyślanie.~~

Faza 4: Pełny Silnik Śledzenia (Execution Trace Engine)
Agent bez przejrzystego logowania to czarna skrzynka, której nikt w biznesie nie zaufa.
- [x] ~~**Rejestrator ścieżki myślowej i wywołań (Trace Collector)**:~~
  ~~Rejestracja w formacie JSONL każdego kroku:~~
  - ~~step: numer kroku~~
  - ~~thought: wewnętrzny Chain-of-Thought agenta~~
  - ~~action_plan: co zamierza wywołać~~
  - ~~tool_call: dokładne parametry~~
  - ~~tool_result_summary: pierwsze 200 znaków odpowiedzi narzędzia~~
  - ~~tokens_used oraz koszt w USD~~
- [x] ~~**Generator wizualnego raportu wykonania (Execution Trace Tree)**:~~
  ~~Eksport pojedynczego przebiegu do czytelnego pliku HTML/Markdown pokazującego drzewo decyzji:~~
  ~~Plan $\to$ Search [OK] $\to$ Scrape [Error 403 $\to$ Fallback do Mocka] $\to$ Synthesis $\to$ Done.~~
- [x] ~~**Wyjście końcowe w restrykcyjnym formacie JSON**:~~
```python
class AccountBrief(BaseModel):
    company_name: str
    value_proposition: str
    estimated_size: str
    verified_sources: List[str]
    tech_stack_detected: List[str]
    sales_triggers: List[str]
    confidence_score: float # 0.0 - 1.0
    missing_information: List[str]
```
Faza 5: Ewaluacja na 25 przypadkach, optymalizacja kosztów i PublikacjaTestujemy agenta na przygotowanym benchmarku i dokumentujemy twarde dane.[ ] Zautomatyzowany Benchmark Runner (run_agent_eval.py):Uruchomienie agenta dla wszystkich 25 firm z Fazy 1 w trybie równoległym (z semaforem).Ewaluacja wygenerowanych briefów przez niezależnego sędziego z Fazy 1 (rubryka binarna 0/1).[ ] Kalkulacja metryk końcowych:Task Success Rate: Odsetek briefów spełniających $\ge 5/6$ kryteriów rubryki.Avg Steps to Completion: Średnia liczba kroków na udane zadanie (optimum: 4–7 kroków).Tool Error Recovery Rate: Ile błędów 4xx/5xx udało się zneutralizować bez wywrotki całego procesu.Cost per Successful Brief: Średni koszt w tokenach i USD za wygenerowany pełny brief.[ ] README z twardymi liczbami (Wyróżnik inżynierski):Wypełnienie sekcji ewaluacyjnej w dokumentacji:Markdown| Metryka | Cel | Wynik BriefAgent |
| :--- | :---: | :---: |
| **Task Success (Rubryka 5/6)** | > 80% | **88.0% (22/25)** |
| **Średnia liczba kroków** | < 8 | **5.4 kroku** |
| **Tool Recovery Rate** | > 75% | **83.3%** |
| **Średni koszt zadania** | < $0.10 | **$0.064** |
| **Zero-Hallucination Rate (Adversarial cases)**| 100% | **100% (3/3 oznaczone jako brak danych)** |