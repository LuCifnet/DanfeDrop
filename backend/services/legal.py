"""
Terms of Service and Legal Information Service
"""
from typing import Dict, Any

def get_terms_of_service() -> Dict[str, Any]:
    return {
        "title": "Terms of Use",
        "last_updated": "September 2026",
        "effective_date": "September 2026",
        "summary": "DanfeDrop is a personal media utility designed for offline preservation and fair use of publicly available content.",
        "sections": [
            {
                "id": "acceptance",
                "title": "1. Acceptance of Terms",
                "content": "By accessing or using DanfeDrop, you agree to comply with and be bound by these Terms of Use. If you do not agree, please discontinue use of the service immediately."
            },
            {
                "id": "permissible-use",
                "title": "2. Permissible & Personal Use",
                "content": "DanfeDrop is provided solely for personal, non-commercial, and educational purposes. You agree to use the service in compliance with all applicable local, national, and international laws, including copyright and intellectual property regulations."
            },
            {
                "id": "copyright",
                "title": "3. Intellectual Property & Copyright",
                "content": "DanfeDrop does not host, store, or own any third-party media content. All video, audio, and metadata belong exclusively to their respective copyright holders. Users are solely responsible for ensuring they possess the appropriate rights, licenses, or fair-use justification for downloading any media."
            },
            {
                "id": "prohibited-activities",
                "title": "4. Prohibited Activities",
                "content": "You agree not to use the service for: commercial redistribution of copyrighted materials, attempting to bypass digital rights management (DRM) or access controls, automated scraping or denial-of-service attacks, or any activity that infringes on third-party rights."
            },
            {
                "id": "disclaimer",
                "title": "5. Disclaimer of Warranties",
                "content": "The application and services are provided 'as is' without warranties of any kind, either express or implied. DanfeDrop makes no guarantees regarding continuous availability, conversion fidelity, or third-party platform compatibility."
            },
            {
                "id": "liability",
                "title": "6. Limitation of Liability",
                "content": "In no event shall the creators, maintainers, or operators of DanfeDrop be held liable for any direct, indirect, incidental, or consequential damages resulting from the use or misuse of this tool."
            }
        ],
        "contact": {
            "support": "support@danfedrop.local",
            "license": "MIT Open Source Utility"
        }
    }
