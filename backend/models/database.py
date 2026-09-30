import os
import sys
import json
import random
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
DB_PATH = os.path.join(PROJECT_ROOT, 'complaints.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Complaint(Base):
    __tablename__ = 'complaints'

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_text = Column(Text, nullable=False)
    clean_text = Column(Text, nullable=True)
    category = Column(String(100), index=True, nullable=False)
    priority = Column(String(50), index=True, nullable=False)
    sentiment = Column(String(50), index=True, nullable=False)
    compound_score = Column(Float, default=0.0)
    emotion = Column(String(50), default='Neutral')
    intent = Column(String(100), default='General Complaint')
    department = Column(String(100), index=True, default='Customer Support')
    risk_level = Column(String(50), index=True, default='Low')
    risk_reasons = Column(Text, default='')
    escalation_recommended = Column(Boolean, default=False)
    escalation_reasons = Column(Text, default='')
    confidence = Column(Float, default=0.0)
    priority_confidence = Column(Float, default=0.0)
    severity_score = Column(Integer, default=50)
    status = Column(String(50), default='Open', index=True)  # Open, In Progress, Resolved, Escalated
    source = Column(String(50), default='Web Portal', index=True)  # Web Portal, Mobile App, Email, Call Center
    customer_name = Column(String(100), default='Customer')
    customer_email = Column(String(150), default='customer@example.com')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)

    analysis = relationship("AnalysisResult", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="complaint", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'complaint_text': self.complaint_text,
            'clean_text': self.clean_text,
            'category': self.category,
            'priority': self.priority,
            'sentiment': self.sentiment,
            'compound_score': self.compound_score,
            'emotion': self.emotion,
            'intent': self.intent,
            'department': self.department,
            'risk_level': self.risk_level,
            'risk_reasons': self.risk_reasons.split(';') if self.risk_reasons else [],
            'escalation_recommended': self.escalation_recommended,
            'escalation_reasons': self.escalation_reasons.split(';') if self.escalation_reasons else [],
            'confidence': self.confidence,
            'priority_confidence': self.priority_confidence,
            'severity_score': self.severity_score,
            'status': self.status,
            'source': self.source,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'resolved_at': self.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if self.resolved_at else None
        }


class AnalysisResult(Base):
    __tablename__ = 'analysis_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey('complaints.id', ondelete='CASCADE'), unique=True, nullable=False)
    entities_json = Column(Text, default='[]')
    keywords_json = Column(Text, default='[]')
    tokens_json = Column(Text, default='[]')
    category_distribution_json = Column(Text, default='[]')
    priority_distribution_json = Column(Text, default='[]')
    suggested_response = Column(Text, default='')
    action_plan = Column(Text, default='')

    complaint = relationship("Complaint", back_populates="analysis")

    def to_dict(self):
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'entities': json.loads(self.entities_json or '[]'),
            'keywords': json.loads(self.keywords_json or '[]'),
            'tokens': json.loads(self.tokens_json or '[]'),
            'category_distribution': json.loads(self.category_distribution_json or '[]'),
            'priority_distribution': json.loads(self.priority_distribution_json or '[]'),
            'suggested_response': self.suggested_response,
            'action_plan': self.action_plan
        }


class KnowledgeArticle(Base):
    __tablename__ = 'knowledge_articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    category = Column(String(100), index=True, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(200), default='')
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'content': self.content,
            'tags': [t.strip() for t in self.tags.split(',') if t.strip()],
            'helpful_count': self.helpful_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Alert(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey('complaints.id', ondelete='CASCADE'), nullable=True)
    alert_type = Column(String(100), index=True, default='High Priority')
    title = Column(String(200), nullable=False)
    description = Column(Text, default='')
    severity = Column(String(50), default='High')  # Critical, High, Medium
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="alerts")

    def to_dict(self):
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'alert_type': self.alert_type,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class ModelRecord(Base):
    __tablename__ = 'model_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    algorithm = Column(String(100), nullable=False)
    accuracy = Column(Float, default=0.0)
    precision = Column(Float, default=0.0)
    recall = Column(Float, default=0.0)
    f1_score = Column(Float, default=0.0)
    dataset_size = Column(Integer, default=0)
    features_count = Column(Integer, default=0)
    trained_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'model_name': self.model_name,
            'algorithm': self.algorithm,
            'accuracy': round(self.accuracy * 100, 2),
            'precision': round(self.precision * 100, 2),
            'recall': round(self.recall * 100, 2),
            'f1_score': round(self.f1_score * 100, 2),
            'dataset_size': self.dataset_size,
            'features_count': self.features_count,
            'trained_at': self.trained_at.strftime('%Y-%m-%d %H:%M:%S') if self.trained_at else None,
            'is_active': self.is_active
        }


def get_db():
    """Database session generator context for Flask routes and services."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(seed=True):
    """Create all tables and seed sample data if database is empty."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        complaint_count = db.query(Complaint).count()
        if complaint_count > 0:
            print(f"[DATABASE] Database already contains {complaint_count} complaints.")
            return

        print("[DATABASE] Empty database detected. Seeding complaints and knowledge base...")

        # 1. Seed Knowledge Base Articles
        articles_data = [
            ("Refund Processing & Bank Settlement SLA", "Payment Issue",
             "Refunds to debit/credit cards typically reflect within 5-7 business days depending on the customer's issuing bank. If the amount was debited twice due to a network glitch, our automated reconciliation engine releases the escrow hold within 24 hours.",
             "refund, payment, deduction, bank, billing"),
            ("Delayed Shipments & Last-Mile Delivery Protocol", "Delivery Issue",
             "Shipments experiencing in-transit delays exceeding 48 hours are automatically escalated to our carrier logistics liaison. Customers can request an address redirect or delivery reschedule via the order tracking portal.",
             "delivery, shipping, courier, package, tracking"),
            ("Damaged or Defective Item Replacement Guidelines", "Product Issue",
             "Customers receiving damaged, defective, or missing items are eligible for immediate replacement upon uploading packaging photos. A pre-paid reverse pickup is scheduled within 24 hours.",
             "damaged, return, replacement, defective, warranty"),
            ("Application Force-Close & Crash Recovery Steps", "Technical Issue",
             "If the mobile or web application crashes during authentication or checkout, clearing local cache, disabling conflicting VPNs, or reinstalling the latest patch resolves 90% of local session corruption errors.",
             "crash, login, bug, error 500, application"),
            ("Compromised Account Protocol & Identity Security", "Account Issue",
             "In suspected account compromise or unauthorized credential modification, accounts are placed under a temporary protective transaction freeze. Resetting via verified SMS OTP restores administrative control.",
             "hacked, security, password, unauthorized, otp"),
            ("Support Ticket Escalation & Executive Review Procedure", "Service Issue",
             "Tickets unresolved beyond agreed SLA parameters or involving inappropriate staff conduct are escalated directly to the Tier-3 Customer Experience Ombudsperson for priority review.",
             "service, agent, escalation, rude, complaint")
        ]

        for title, cat, content, tags in articles_data:
            art = KnowledgeArticle(title=title, category=cat, content=content, tags=tags, helpful_count=random.randint(5, 50))
            db.add(art)

        # 2. Seed Complaints from dataset/complaints.csv
        import csv
        from nlp.preprocessing import preprocess_text
        from nlp.sentiment import analyze_sentiment

        csv_path = os.path.join(PROJECT_ROOT, 'dataset', 'complaints.csv')
        if os.path.exists(csv_path):
            first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Robin", "Casey", "Avery", "Priya", "Rahul", "Ananya", "Rohan", "Elena", "Liam"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Sharma", "Verma", "Patel", "Garcia", "Rodriguez", "Wilson"]
            sources = ["Web Portal", "Mobile App", "Email", "Customer Care"]
            statuses = ["Resolved", "Resolved", "In Progress", "Open", "Open"]

            dept_map = {
                'Payment Issue': 'Fintech & Billing Reconciliation Desk',
                'Delivery Issue': 'Logistics & Courier Dispatch Operations',
                'Product Issue': 'Quality Assurance & Returns Verification Desk',
                'Technical Issue': 'Tier-2 Engineering & Application Bug Triage',
                'Account Issue': 'Identity Security & User Access Control',
                'Service Issue': 'Customer Experience & Executive Escalations'
            }

            intent_map = {
                'Payment Issue': 'Refund Request',
                'Delivery Issue': 'Delivery Tracking / Expedite',
                'Product Issue': 'Replacement Request',
                'Technical Issue': 'Bug Report & Technical Support',
                'Account Issue': 'Account Access & Password Recovery',
                'Service Issue': 'Service Escalation'
            }

            emotion_map = {
                'High': 'Anger',
                'Medium': 'Frustration',
                'Low': 'Neutral'
            }

            now = datetime.utcnow()

            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            for i, row in enumerate(rows):
                raw_text = row['complaint']
                cat = row['category']
                prio = row['priority']

                clean = preprocess_text(raw_text)
                sent_res = analyze_sentiment(raw_text)
                sentiment = sent_res['sentiment']
                compound = sent_res['compound_score']

                # Realistic date over the past 45 days
                days_ago = random.randint(0, 45)
                hours_ago = random.randint(0, 23)
                mins_ago = random.randint(0, 59)
                created_date = now - timedelta(days=days_ago, hours=hours_ago, minutes=mins_ago)

                status = random.choice(statuses)
                resolved_date = created_date + timedelta(hours=random.randint(2, 48)) if status == 'Resolved' else None

                name = f"{random.choice(first_names)} {random.choice(last_names)}"
                email = f"{name.lower().replace(' ', '.')}@example.com"

                # Risk & escalation
                risk = 'Low'
                risk_reasons = []
                escalate = False
                escalate_reasons = []

                if prio == 'High':
                    risk = 'High' if sentiment != 'Negative' else 'Critical'
                    risk_reasons.append('High priority classification')
                    if 'hacked' in raw_text.lower() or 'stolen' in raw_text.lower():
                        risk = 'Critical'
                        risk_reasons.append('Account security vulnerability identified')
                        escalate = True
                        escalate_reasons.append('Security breach alert')
                    if 'deducted twice' in raw_text.lower() or 'fraud' in raw_text.lower():
                        risk_reasons.append('Direct financial transaction dispute')
                        escalate = True
                        escalate_reasons.append('Immediate financial refund request')
                elif prio == 'Medium':
                    risk = 'Medium'
                    risk_reasons.append('Operational service interruption')

                # Calculate severity score
                base_prio = {'High': 75, 'Medium': 48, 'Low': 20}[prio]
                sev_score = max(10, min(100, base_prio + int(abs(compound) * 20) if compound < 0 else base_prio))

                complaint = Complaint(
                    complaint_text=raw_text,
                    clean_text=clean,
                    category=cat,
                    priority=prio,
                    sentiment=sentiment,
                    compound_score=compound,
                    emotion=emotion_map.get(prio, 'Neutral'),
                    intent=intent_map.get(cat, 'General Complaint'),
                    department=dept_map.get(cat, 'Customer Support'),
                    risk_level=risk,
                    risk_reasons=';'.join(risk_reasons),
                    escalation_recommended=escalate,
                    escalation_reasons=';'.join(escalate_reasons),
                    confidence=round(random.uniform(0.65, 0.94), 3),
                    priority_confidence=round(random.uniform(0.60, 0.88), 3),
                    severity_score=sev_score,
                    status=status,
                    source=random.choice(sources),
                    customer_name=name,
                    customer_email=email,
                    created_at=created_date,
                    resolved_at=resolved_date
                )
                db.add(complaint)
                db.flush()

                # Add AnalysisResult
                analysis = AnalysisResult(
                    complaint_id=complaint.id,
                    tokens_json=json.dumps(clean.split()),
                    keywords_json=json.dumps([w for w in clean.split() if len(w) > 3][:5]),
                    entities_json=json.dumps([{"type": "CATEGORY", "value": cat}]),
                    category_distribution_json=json.dumps([{"name": cat, "probability": 0.82}]),
                    priority_distribution_json=json.dumps([{"name": prio, "probability": 0.78}]),
                    suggested_response=f"Dear {name}, we sincerely apologize for the inconvenience regarding your {cat.lower()}. Our {dept_map.get(cat)} has received your ticket and is actively addressing it.",
                    action_plan=f"Investigate customer ticket #{complaint.id} and resolve within target SLA."
                )
                db.add(analysis)

                # Add alert for critical/escalated
                if escalate or risk == 'Critical':
                    alert = Alert(
                        complaint_id=complaint.id,
                        alert_type='Critical Security/Financial Risk',
                        title=f"Critical Incident: #{complaint.id} - {cat}",
                        description=f"High risk complaint from {name}: {raw_text[:120]}...",
                        severity='Critical',
                        is_read=False,
                        created_at=created_date
                    )
                    db.add(alert)

            db.commit()
            print(f"[DATABASE] Successfully seeded {len(rows)} complaints with full relational data.")

    except Exception as e:
        db.rollback()
        print(f"[DATABASE ERROR] Error during init_db: {str(e)}")
    finally:
        db.close()


if __name__ == '__main__':
    init_db(seed=True)
