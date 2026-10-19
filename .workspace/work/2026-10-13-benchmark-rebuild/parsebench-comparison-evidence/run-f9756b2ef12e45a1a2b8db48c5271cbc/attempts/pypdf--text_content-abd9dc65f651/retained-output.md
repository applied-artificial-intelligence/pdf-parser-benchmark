Have Your Say: Best Practice Consultation 
Best practice guidance for 
reporting AI usage Problem statement 
Release 5.1 of the COUNTER Code of Practice was developed prior to the public availability of 
generative and agentic artiﬁcial intelligence. In 2025 we started developing these best practice 
guidelines, drawing on the existing Extensions protocol outlined in Section 11 
(https://cop5.countermetrics.org/en/5.1.0.1/11-extending/index.html), to facilitate reporting on AI 
usage.  
These guidelines apply primarily to AI tools on publisher platforms: third-party and oﬀ-site tools like 
ChatGPT, Consensus or Perplexity may ﬁnd the guidelines useful in conjunction with our existing 
Syndicated Usage best practices. 
Distinguishing between human, bot and agentic usage 
Section 7.8 of the Code of Practice states that activity that is not initiated by human users SHOULD 
NOT be included in COUNTER usage reports. That is, only human usage should be included, whether 
that’s actual humans or humans running text and data mining activity (which must be tracked per 
Section 7.10). That rule was created before the advent of easy access to AI agents. We are aware that 
AI agents are not the same as the bots and crawlers that we have historically excluded from 
reporting. We have addressed that issue in the guidance.  
Using Extensions to report on AI usage 
This section of the best practice guidance sets out our recommendations for using the Extensions 
protocol laid out in Section 11.4 of the Code of Practice to best report on AI usage. This relies on 
report providers using shared custom elements for reporting agentic usage. 
Extension one: Access_Method 
For reporting agentic usage, report providers should apply the principles of Section 11.4 by adding a 
reserved Access_Method: Agent. 
Adding this extension is the simplest technical solution for the question of reporting on agentic 
usage.  
Potential extension two: Metric_Type 
For reporting agentic usage, report providers could apply the principles of Section 11.4 by using 
reserved Metric_Types: