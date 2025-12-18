from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from typing import Optional  # Add this
from pydantic import BaseModel
from backend.services.llm import generate_cover_letter_content
from backend.services.document import create_pdf_stream

app = FastAPI(title="Cover Letter Generator API")

# --- Data Models ---
class OfferData(BaseModel):
    job_title: str
    company_name: str
    language: str
    offer_description: str
    user_name: Optional[str] = ""
    user_email: Optional[str] = ""
    user_phone: Optional[str] = ""


class LetterData(BaseModel):
    job_title: str
    company_name: str
    edited_letter: str
    language: str
    user_name: Optional[str] = ""
    user_email: Optional[str] = ""
    user_phone: Optional[str] = ""

# --- Endpoints ---
@app.post("/generate-letter")
async def generate_letter(offer: OfferData):
    try:
        content = generate_cover_letter_content(
            job_title=offer.job_title,
            company_name=offer.company_name,
            language=offer.language,
            description=offer.offer_description,
            user_name=offer.user_name
        )
        return {"letter": content}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-pdf")
async def generate_pdf(data: LetterData):
    try:
        pdf_bytes = create_pdf_stream(
            job_title=data.job_title,
            edited_letter=data.edited_letter,
            language=data.language,
            user_data={  # Bundle user data
                "name": data.user_name,
                "email": data.user_email,
                "phone": data.user_phone
            }
        )

        # Return file as a binary stream with correct headers
        filename = f"Cover_Letter_{data.company_name.replace(' ', '_')}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))
