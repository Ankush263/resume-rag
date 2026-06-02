# Plan

## Chunking strategy
For resumes and JDs, chunking should not be random.

### Resume chunking
Split by sections:

```
Summary
Skills
Experience
Projects
Education
Certifications
Achievements
```

Then split experience into bullet-level chunks.

eg.
```
{
  "source_type": "resume",
  "section": "Experience",
  "company": "Circle Health",
  "content": "Built OCR pipeline using Gemini to extract patient health report data and generate structured health charts.",
  "metadata": {
    "role": "Full-stack Developer",
    "page": 1
  }
}
```

### JD chunking
Split by:
```
Company Overview
Role Summary
Responsibilities
Required Skills
Preferred Skills
Experience Requirements
Benefits
```
eg. 
```
{
  "source_type": "job_description",
  "section": "Required Skills",
  "content": "Candidate should have experience building RAG systems, vector search, prompt optimization, and production AI workflows."
}
```
### Best chunk size

```
Resume chunks: 100–250 words
JD chunks: 150–350 words
Overlap: 30–50 words
```

## Retrieval design

Do not use one generic retriever for every question. Use task-specific retrieval.

`Question: “How well do I match this job?”`

```
Top JD chunks:
- Required skills
- Responsibilities
- Experience requirements

Top resume chunks:
- Skills
- Experience
- Projects
```

`Question: “Which resume bullets should I improve?”`

```
JD required skills + responsibilities
Resume experience bullets + projects
```

`Question: “What interview questions should I prepare?”`

```
JD responsibilities
JD required skills
Resume claims that match those skills
```

`Question: “Write a cover letter based on the JD.”`

```
JD company/role summary
JD responsibilities
Resume strongest matching projects/experience
```