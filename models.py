"""
Database models for AURA Research Assistant
"""

import json
from datetime import datetime
from app import db

class ResearchProject(db.Model):
    """Research project model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    queries = db.relationship('ResearchQuery', backref='project', lazy=True, cascade="all, delete-orphan")
    papers = db.relationship('Paper', backref='project', lazy=True, cascade="all, delete-orphan")
    hypotheses = db.relationship('Hypothesis', backref='project', lazy=True, cascade="all, delete-orphan")
    chat_messages = db.relationship('ChatMessage', backref='project', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ResearchProject {self.id}: {self.title}>"

class ResearchQuery(db.Model):
    """Research query model"""
    id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.id'), nullable=False)
    
    # Relationships
    papers = db.relationship('Paper', backref='query', lazy=True)
    
    def __repr__(self):
        return f"<ResearchQuery {self.id}: {self.query_text[:50]}>"

class Paper(db.Model):
    """Research paper model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.Text)  # Stored as JSON
    abstract = db.Column(db.Text)
    url = db.Column(db.String(512))
    pdf_url = db.Column(db.String(512))
    published_date = db.Column(db.DateTime)
    source = db.Column(db.String(50))  # arxiv, semantic_scholar, etc.
    external_id = db.Column(db.String(100))  # ID from the source
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional data
    metadata = db.Column(db.Text)  # Stores additional metadata as JSON
    
    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.id'), nullable=False)
    query_id = db.Column(db.Integer, db.ForeignKey('research_query.id'))
    
    # Relationships
    summary = db.relationship('PaperSummary', backref='paper', uselist=False, cascade="all, delete-orphan")
    
    def set_metadata(self, metadata_dict):
        """Set metadata as JSON"""
        self.metadata = json.dumps(metadata_dict)
    
    def get_metadata(self):
        """Get metadata as Python dictionary"""
        if self.metadata:
            return json.loads(self.metadata)
        return {}
    
    def set_authors(self, authors_list):
        """Set authors as JSON"""
        self.authors = json.dumps(authors_list)
    
    def get_authors(self):
        """Get authors as Python list"""
        if self.authors:
            return json.loads(self.authors)
        return []
    
    def __repr__(self):
        return f"<Paper {self.id}: {self.title}>"

class PaperSummary(db.Model):
    """Paper summary model"""
    id = db.Column(db.Integer, primary_key=True)
    summary_text = db.Column(db.Text)
    key_findings = db.Column(db.Text)  # Stored as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), nullable=False)
    
    def set_key_findings(self, findings_list):
        """Set key findings as JSON"""
        self.key_findings = json.dumps(findings_list)
    
    def get_key_findings(self):
        """Get key findings as Python list"""
        if self.key_findings:
            return json.loads(self.key_findings)
        return []
    
    def __repr__(self):
        return f"<PaperSummary {self.id} for Paper {self.paper_id}>"

class Hypothesis(db.Model):
    """Research hypothesis model"""
    id = db.Column(db.Integer, primary_key=True)
    hypothesis_text = db.Column(db.Text, nullable=False)
    reasoning = db.Column(db.Text)
    confidence_score = db.Column(db.Float)  # 0-1 scale
    supporting_evidence = db.Column(db.Text)  # JSON list of paper IDs and relevant quotes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.id'), nullable=False)
    
    # Relationships
    experiments = db.relationship('ExperimentDesign', backref='hypothesis', lazy=True)
    
    def set_supporting_evidence(self, evidence_dict):
        """Set supporting evidence as JSON"""
        self.supporting_evidence = json.dumps(evidence_dict)
    
    def get_supporting_evidence(self):
        """Get supporting evidence as Python dictionary"""
        if self.supporting_evidence:
            return json.loads(self.supporting_evidence)
        return {}
    
    def __repr__(self):
        return f"<Hypothesis {self.id}: {self.hypothesis_text[:50]}>"

class ExperimentDesign(db.Model):
    """Experiment design model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    methodology = db.Column(db.Text)
    variables = db.Column(db.Text)  # JSON structure for independent/dependent variables
    controls = db.Column(db.Text)
    expected_outcomes = db.Column(db.Text)
    limitations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    hypothesis_id = db.Column(db.Integer, db.ForeignKey('hypothesis.id'), nullable=False)
    
    def set_variables(self, variables_dict):
        """Set variables as JSON"""
        self.variables = json.dumps(variables_dict)
    
    def get_variables(self):
        """Get variables as Python dictionary"""
        if self.variables:
            return json.loads(self.variables)
        return {}
    
    def __repr__(self):
        return f"<ExperimentDesign {self.id}: {self.title}>"

class ChatMessage(db.Model):
    """Chat message model"""
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  # user, system, agent
    content = db.Column(db.Text, nullable=False)
    agent_type = db.Column(db.String(50))  # retrieval, summarization, hypothesis, experiment, tensorflow
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.id'), nullable=False)
    
    def __repr__(self):
        return f"<ChatMessage {self.id} ({self.role}): {self.content[:50]}>"