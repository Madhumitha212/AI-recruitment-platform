from pathlib import Path
from fastapi import APIRouter
from fastapi import UploadFile, File
from parser.text_reader import TextReader
from typing import Annotated, List
from parser.pdf_parser import PDFParser
from orchestrator.agent_orchestrator import AgentOrchestrator
from fastapi import HTTPException

router = APIRouter()
orchestrator = AgentOrchestrator()

RESUME_DIR = Path("uploads/resumes")
JD_DIR = Path("uploads/jd")

RESUME_DIR.mkdir(parents=True, exist_ok=True)
JD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-resumes")
async def upload_resumes(
    resumes: Annotated[
        List[UploadFile],
        File(description="Upload multiple PDF resumes")
    ]
):
    parsed_resumes = []

    for resume in resumes:
        file_path = RESUME_DIR / resume.filename

        content = await resume.read()

        with open(file_path, "wb") as f:
            f.write(content)

        text = PDFParser.extract_text(str(file_path))

        parsed_resumes.append(
            {
                "file_name": resume.filename,
                "text_length": len(text),
                "preview": text[:500]
            }
        )

    return {
        "message": "Resumes uploaded successfully",
        "total_resumes": len(parsed_resumes),
        "resumes": parsed_resumes
    }


@router.post("/upload-jd")
async def upload_jd(
        jd: UploadFile = File(...)
):

    if not jd.filename.endswith(".txt"):
        return {
            "error": "Only .txt files are allowed for Job Description"
        }

    file_path = JD_DIR / jd.filename

    content = await jd.read()

    with open(file_path, "wb") as f:
        f.write(content)

    text = TextReader.read_text(str(file_path))

    return {
        "message": "JD uploaded successfully",
        "file_name": jd.filename,
        "text_length": len(text),
        "preview": text[:500]
    }


@router.post("/evaluate-candidates")
async def evaluate_candidates():

    try:

        # -------------------------
        # Check Resume Files
        # -------------------------
        resume_files = list(
            RESUME_DIR.glob("*.pdf")
        )

        if not resume_files:
            raise HTTPException(
                status_code=404,
                detail="No resume files found in uploads/resumes"
            )

        # -------------------------
        # Check JD Files
        # -------------------------
        jd_files = list(
            JD_DIR.glob("*.txt")
        )

        if not jd_files:
            raise HTTPException(
                status_code=404,
                detail="No JD file found in uploads/jd"
            )

        # -------------------------
        # Read JD
        # -------------------------
        try:

            jd_text = TextReader.read_text(
                str(jd_files[0])
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"JD Reading Failed: {str(e)}"
            )

        if not jd_text.strip():

            raise HTTPException(
                status_code=400,
                detail="JD file is empty"
            )

        results = []

        # -------------------------
        # Process Every Resume
        # -------------------------
        for resume_file in resume_files:

            try:

                resume_text = PDFParser.extract_text(
                    str(resume_file)
                )

                if not resume_text.strip():

                    results.append(
                        {
                            "resume": resume_file.name,
                            "status": "FAILED",
                            "reason": "Empty Resume Text"
                        }
                    )

                    continue

                evaluation = await orchestrator.evaluate_candidate(
                    resume_text,
                    jd_text
                )

                results.append(
                    {
                        "resume": resume_file.name,
                        "status": "SUCCESS",
                        "evaluation": evaluation
                    }
                )

            except KeyError as e:

                results.append(
                    {
                        "resume": resume_file.name,
                        "status": "FAILED",
                        "reason": f"Missing Key: {str(e)}"
                    }
                )

            except Exception as e:

                results.append(
                    {
                        "resume": resume_file.name,
                        "status": "FAILED",
                        "reason": str(e)
                    }
                )

        
        # ====================================
        # Separate Successful Candidates
        # ====================================

        successful_results = [
            r for r in results
            if r["status"] == "SUCCESS"
        ]

        failed_candidates = [
            r for r in results
            if r["status"] == "FAILED"
        ]

        # ====================================
        # Ranking Logic
        # ====================================

        decision_priority = {
            "SHORTLIST": 3,
            "HOLD": 2,
            "REJECT": 1
        }

        successful_results.sort(
            key=lambda x: (
                decision_priority.get(
                    x["evaluation"]["recommendation"]["decision"],
                    0
                ),
                x["evaluation"]["match_report"][
                    "match_percentage"
                ]
            ),
            reverse=True
        )

        # ====================================
        # Assign Rank
        # ====================================

        for rank, candidate in enumerate(
            successful_results,
            start=1
        ):
            candidate["rank"] = rank

        # ====================================
        # Separate By Decision
        # ====================================

        shortlisted_candidates = [
            candidate
            for candidate in successful_results
            if candidate["evaluation"]
            ["recommendation"]["decision"]
            == "SHORTLIST"
        ]

        hold_candidates = [
            candidate
            for candidate in successful_results
            if candidate["evaluation"]
            ["recommendation"]["decision"]
            == "HOLD"
        ]

        rejected_candidates = [
            candidate
            for candidate in successful_results
            if candidate["evaluation"]
            ["recommendation"]["decision"]
            == "REJECT"
        ]

        # ====================================
        # Summary
        # ====================================

        summary = {
            "total_candidates": len(resume_files),
            "shortlisted_count": len(
                shortlisted_candidates
            ),
            "hold_count": len(
                hold_candidates
            ),
            "rejected_count": len(
                rejected_candidates
            ),
            "failed_count": len(
                failed_candidates
            )
        }

        # ====================================
        # Final Response
        # ====================================

        return {

            "summary": summary,

            "shortlisted_candidates":
                shortlisted_candidates,

            "hold_candidates":
                hold_candidates,

            "rejected_candidates":
                rejected_candidates,

            "failed_candidates":
                failed_candidates
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )


# @router.post("/analyze-resume")
# async def analyze_resume():

#     sample_resume = """
#     John Doe

#     Skills:
#     Java
#     Spring Boot
#     SQL

#     Education:
#     B.Tech Computer Science

#     Experience:
#     2 Years Java Developer

#     Projects:
#     Library Management System

#     Certifications:
#     Oracle Java Certification
#     """

#     profile = await orchestrator.analyze_resume(
#         sample_resume
#     )

#     return profile

# @router.get("/analyze-jd")
# async def analyze_jd():

#     sample_jd = """
#     Role: Java Developer

#     Required Skills:
#     Java
#     Spring Boot
#     SQL

#     Preferred Skills:
#     Docker
#     AWS

#     Experience:
#     0-2 Years

#     Education:
#     B.Tech
#     """

#     result = await orchestrator.analyze_jd(
#         sample_jd
#     )

#     return {
#         "jd_analysis": result
#     }

# @router.get("/evaluate")
# async def evaluate():

#     resume_text = """
#     John Doe

#     Skills:
#     Java
#     Spring Boot
#     SQL
#     """

#     jd_text = """
#     Role: Java Developer

#     Required Skills:
#     Java
#     SQL
#     Spring Boot
#     Docker
#     """

#     result = await orchestrator.evaluate_candidate(
#         resume_text,
#         jd_text
#     )

#     return result

# @router.get("/test-jd")
# async def test_jd():

#     jd_text = """
#     Role: Java Developer

#     Required Skills:
#     Java
#     Spring Boot
#     SQL

#     Preferred Skills:
#     Docker
#     AWS

#     Experience:
#     0-2 Years

#     Education:
#     B.Tech
#     """

#     result = await orchestrator.analyze_jd(jd_text)

#     print(type(result))
#     print(result)

#     return result

# @router.get("/test-resume")
# async def test_resume():

#     resume_text = """
#     John Doe

#     Skills:
#     Java
#     Spring Boot
#     SQL

#     Education:
#     B.Tech

#     Experience:
#     2 Years

#     Projects:
#     Library Management System

#     Certifications:
#     Oracle Java
#     """

#     result = await orchestrator.analyze_resume(resume_text)

#     print(type(result))
#     print(result)

#     return result