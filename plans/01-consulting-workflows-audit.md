# Consulting Workflows Audit & Implementation Plan

**Date**: February 3, 2026  
**Status**: Complete Analysis  
**Target**: Comprehensive consulting and custom software development workflows with all required forms and documents

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Implementation Status](#current-implementation-status)
3. [Industry Standards Gap Analysis](#industry-standards-gap-analysis)
4. [Missing Forms and Documents](#missing-forms-and-documents)
5. [Phase-by-Phase Implementation Plan](#phase-by-phase-implementation-plan)

---

## Executive Summary

### What Votra.io Currently Has

The platform currently implements a **foundational consulting workflow** with these core entities:

- ✅ **Client Management** (clients router/service/models)
- ✅ **SOW Management** (sows router/service/models with approval workflow)
- ✅ **Project Management** (projects router/service/models)
- ✅ **Timesheet Management** (timesheets router/service/models with billing)
- ✅ **Invoice Generation** (invoices router/service/models)
- ✅ **Basic Reporting** (reports router/service)
- ✅ **Audit Logging** (AuditLog database model)
- ✅ **RBAC** (role-based access control with Admin, ProjectManager, Consultant, Client, Accountant roles)

### Key Gaps Against Industry Standards

Based on consulting industry best practices (AICPA, professional services standards, PMBOK), the platform is **missing critical forms and workflows**:

**Critical Gap 1: Client Onboarding & Legal**
- ❌ Master Service Agreement (MSA) templates
- ❌ NDA workflows
- ❌ Client questionnaire/intake forms
- ❌ Payment terms and billing contact management
- ❌ Contract signature tracking
- ❌ Client engagement change orders

**Critical Gap 2: Resource Management**
- ❌ Resource allocation and scheduling forms
- ❌ Consultant availability/capacity planning
- ❌ Skill matrix and certification tracking
- ❌ Resource conflict detection
- ❌ Team composition in SOWs

**Critical Gap 3: Scope & Change Management**
- ❌ Scope baseline documentation
- ❌ Change request forms and approval workflow
- ❌ Scope amendment process
- ❌ Out-of-scope tracking
- ❌ Change impact analysis

**Critical Gap 4: Financial & Risk**
- ❌ Expense tracking and cost allocation
- ❌ Project profitability analysis (basic exists, needs enhancement)
- ❌ Budget variance analysis
- ❌ Risk register and contingency planning
- ❌ Quote/Proposal generation
- ❌ Payment term flexibility (net 30/45/60, deposits, milestones)

**Critical Gap 5: Project Governance**
- ❌ Approval workflows (multi-level sign-offs)
- ❌ Status reports and dashboards
- ❌ Meeting notes and action items
- ❌ Risks and issues log
- ❌ Stakeholder communication log
- ❌ Project milestones and gates

**Critical Gap 6: Custom Software Development Specific**
- ❌ Technical requirements specification (TRS) forms
- ❌ Architecture documentation templates
- ❌ Code review checklists
- ❌ Release management and deployment checklists
- ❌ UAT planning and tracking
- ❌ Defect/bug tracking
- ❌ Knowledge transfer documentation
- ❌ Production support handoff forms

**Critical Gap 7: Compliance & Legal**
- ❌ Data security and privacy agreements
- ❌ IP ownership agreements
- ❌ Compliance attestation forms (SOC 2, ISO 27001, etc.)
- ❌ Audit trail reporting for financial/legal
- ❌ Retention policy enforcement
- ❌ Export/deletion request workflows

**Critical Gap 8: Client Portal**
- ❌ Client-facing dashboard
- ❌ Project visibility (read-only for clients)
- ❌ Invoice and payment tracking
- ❌ Document repository/sharing
- ❌ Client approval workflows

---

## Current Implementation Status

### Database Models (Implemented ✅)

| Model | Status | Details |
|-------|--------|---------|
| User | ✅ Complete | Roles: admin, project_manager, consultant, client, accountant |
| Client | ✅ Complete | Basic contact and payment term info |
| SOW | ✅ Complete | Status: draft, pending, approved, rejected, completed |
| Project | ✅ Complete | Tied to SOW, budget tracking |
| Timesheet | ✅ Complete | Billable tracking, invoice linking |
| Invoice | ✅ Complete | Line items, basic payment tracking |
| LineItem | ✅ Complete | Associated with invoices |
| AuditLog | ✅ Complete | Change tracking |

### API Endpoints (Implemented ✅)

**Clients (`/api/v1/clients/*`)**
- ✅ POST / - Create client
- ✅ GET / - List clients (paginated)
- ✅ GET /{id} - Get client details
- ✅ PUT /{id} - Update client
- ✅ DELETE /{id} - Archive client

**SOWs (`/api/v1/sows/*`)**
- ✅ POST / - Create SOW (draft)
- ✅ GET / - List SOWs (filtered by status)
- ✅ GET /{id} - Get SOW details
- ✅ PUT /{id} - Update SOW
- ✅ POST /{id}/approve - Approve SOW (PM/Admin)
- ✅ POST /{id}/reject - Reject SOW with notes
- ✅ GET /{id}/projects - Get projects from SOW

**Projects (`/api/v1/projects/*`)**
- ✅ POST / - Create project from approved SOW
- ✅ GET / - List projects (paginated)
- ✅ GET /{id} - Get project details
- ✅ PUT /{id} - Update project description
- ✅ POST /{id}/complete - Mark project complete

**Timesheets (`/api/v1/timesheets/*`)**
- ✅ POST / - Submit timesheet
- ✅ GET / - List timesheets (filtered)
- ✅ GET /{id} - Get timesheet
- ✅ PUT /{id} - Update timesheet (before approval)
- ✅ POST /{id}/approve - Approve timesheet (PM/Admin)
- ✅ DELETE /{id} - Delete timesheet

**Invoices (`/api/v1/invoices/*`)**
- ✅ POST / - Generate invoice from approved timesheets
- ✅ GET / - List invoices
- ✅ GET /{id} - Get invoice details
- ✅ PUT /{id} - Update invoice (before sending)
- ✅ POST /{id}/send - Mark invoice as sent
- ✅ POST /{id}/record-payment - Record payment

**Reports (`/api/v1/reports/*`)**
- ✅ GET /project-hours - Hours by project
- ✅ GET /consultant-utilization - Utilization rates
- ✅ GET /profitability - Project profitability
- ✅ GET /revenue - Revenue tracking
- ✅ GET /outstanding-invoices - Payment aging

### Pydantic Models (Implemented ✅)

All models follow Pydantic v2 with:
- ✅ Request/response separation
- ✅ Field validation (min_length, max_length, gt, ge, le, etc.)
- ✅ Decimal types for currency
- ✅ Date/datetime handling
- ✅ Custom validators
- ✅ Response configuration (from_attributes=True)

### Testing (Implemented ✅)

- ✅ Test files for all major routers (clients, SOWs, projects, timesheets, invoices)
- ✅ pytest fixtures and conftest
- ✅ Target: 80%+ coverage
- ✅ Audit tests implemented

---

## Industry Standards Gap Analysis

### 1. AICPA Professional Services Standards

**What Industry Expects:**
- Formal SOW with clear scope boundaries
- Client approval signatures
- Change management process for scope changes
- Documented resource allocation
- Regular status reporting
- Financial tracking and reporting
- Risk management and escalation procedures

**Votra.io Status:**
- ✅ SOW with approval (but no signatures)
- ✅ Basic scope in SOW description (needs detail)
- ❌ Formal change management process
- ❌ Resource allocation tracking
- ❌ Status reporting forms
- ❌ Formal risk management
- ⚠️ Financial tracking exists but needs enhancement

### 2. Project Management Institute (PMBOK) Standards

**What Industry Expects:**
- Project charter with objectives and success criteria
- Scope statement with inclusions/exclusions
- Work breakdown structure (WBS)
- Resource management plan
- Risk register
- Communication plan
- Stakeholder management
- Change log
- Project milestones and gates

**Votra.io Status:**
- ❌ No formal project charter
- ⚠️ Scope in SOW description (unstructured)
- ❌ No WBS
- ❌ No resource plan
- ❌ No risk register
- ❌ No communication plan
- ❌ No stakeholder register
- ❌ No formal change log
- ❌ No milestone tracking

### 3. Professional Services Automation (PSA) Platform Standards

**What Industry Expects:**
- Multi-level approval workflows
- Resource capacity planning
- Time and expense tracking with detailed categorization
- Project profitability analysis
- Quote/proposal generation
- Milestone-based billing
- Expense allocation and cost tracking
- Utilization reporting
- Client portal with visibility
- Formal contracts/MSA management

**Votra.io Status:**
- ⚠️ Basic approval (needs multi-level)
- ❌ No capacity planning
- ⚠️ Time tracking exists (expenses missing)
- ⚠️ Profitability basic (needs enhancement)
- ❌ No quote/proposal generation
- ❌ Milestone billing not supported
- ❌ No expense tracking
- ⚠️ Basic utilization reports exist
- ❌ No client portal
- ❌ No MSA/contract management

### 4. Software Development Custom Projects Specifics

**What Industry Expects:**
- Technical requirements specification (TRS)
- Architecture/design documentation
- Code review process and tracking
- Release management process
- UAT (User Acceptance Testing) planning and execution
- Defect tracking and resolution
- Knowledge transfer documentation
- Production support and maintenance planning
- Post-implementation review (PIR)

**Votra.io Status:**
- ❌ No TRS system
- ❌ No design documentation tracking
- ❌ No code review tracking
- ❌ No release management
- ❌ No UAT planning
- ❌ No defect tracking
- ❌ No knowledge transfer docs
- ❌ No support planning
- ❌ No PIR system

### 5. Legal & Compliance

**What Industry Expects:**
- Master Service Agreement (MSA) templates
- NDA tracking and management
- IP ownership agreements
- Data security and privacy agreements
- Client questionnaire/intake forms
- Engagement letters
- Compliance attestations (SOC 2, ISO, HIPAA, etc.)
- Legal contract version control
- Signature tracking

**Votra.io Status:**
- ❌ No MSA system
- ❌ No NDA system
- ❌ No IP agreement tracking
- ❌ No data security agreement
- ❌ No intake forms
- ❌ No engagement letters
- ❌ No compliance tracking
- ❌ No version control for contracts
- ❌ No signature tracking

---

## Missing Forms and Documents

### Priority 1: Critical Forms (Blocks Revenue & Legal Risk)

#### P1.1 Master Service Agreement (MSA) Management
- **Purpose**: Legal framework for client relationships
- **Frontend**: 
  - Template selection/customization UI
  - MSA upload and version history
  - Signature tracking dashboard
  - Expiration/renewal alerts
- **Backend Models**:
  - `MSA` - Contains template, versions, status, signatures
  - `MSASignature` - Track signatures with date/by whom
  - `MSAVersion` - Version control
- **Rules**:
  - MSA required before SOW creation
  - Signature required before invoice generation (optional per config)
  - Version history maintained
  - Auto-alerts 30 days before expiration

#### P1.2 Change Order Form
- **Purpose**: Track scope changes and authorization
- **Frontend**: 
  - Change request form (description, impact, cost change)
  - Approval workflow UI
  - Change order history on project
  - Impact analysis dashboard
- **Backend Models**:
  - `ChangeOrder` - Links to SOW/Project, tracks scope/budget changes
  - `ChangeOrderApproval` - Multi-level approval tracking
- **Rules**:
  - Auto-calculates new SOW budget
  - Requires PM + Client approval
  - Creates new SOW version if major change
  - Prevents invoice on unapproved changes

#### P1.3 Client Intake Form
- **Purpose**: Comprehensive client onboarding
- **Frontend**: 
  - Questionnaire form (company, contacts, preferences)
  - Document upload (certifications, security forms)
  - Compliance requirement checkboxes
  - Legal entity information
- **Backend Models**:
  - `ClientIntake` - Stores completed intake info
  - `ClientDocument` - Uploaded documents with versions
  - `ComplianceRequirement` - Tracks client's compliance needs
- **Rules**:
  - Required before first SOW
  - Triggering compliance checklist creation
  - Document expiration tracking

#### P1.4 NDA Management
- **Purpose**: Legal protection for both parties
- **Frontend**: 
  - NDA template selection
  - Signature workflow
  - NDA status dashboard per client
  - Expiration tracking
- **Backend Models**:
  - `NDA` - Client's NDA with status and expiration
  - `NDASignature` - Signature tracking
- **Rules**:
  - Required before discussing sensitive scopes
  - Auto-alert 30 days before expiration
  - Blocks SOW creation if required but not signed

### Priority 2: High-Value Forms (Revenue Impact & Standard Practice)

#### P2.1 Quote/Proposal Form
- **Purpose**: Formal quote before SOW creation
- **Frontend**: 
  - Quote builder from templates
  - Dynamic pricing based on scope
  - Client preview with branding
  - PDF export and email
- **Backend Models**:
  - `Quote` - Base quote info
  - `QuoteLineItem` - Scope items with pricing
  - `QuoteVersion` - Version history
  - `QuoteStatus` - Accepted, Declined, Expired
- **Rules**:
  - Quote conversion to SOW (one-click)
  - Quote expiration (30 days default)
  - QuoteLineItem links to SOW scope when converted
  - Version control for negotiation

#### P2.2 Resource Plan & Allocation Form
- **Purpose**: Track consultant allocation and capacity
- **Frontend**: 
  - Resource matrix by project
  - Consultant availability calendar
  - Skill-based resource search
  - Allocation conflict detection
  - Utilization dashboard
- **Backend Models**:
  - `ResourceAllocation` - Links user to project with allocation %
  - `ConsultantSkill` - User's skills and certifications
  - `ConsultantCapacity` - Availability by week/month
  - `AllocationConflict` - Detected double-booking
- **Rules**:
  - Total allocation can't exceed 100% per consultant
  - Flagging conflicts for PM
  - Automatic conflict detection
  - Historical tracking of allocations

#### P2.3 Project Milestones & Gates
- **Purpose**: Track deliverables and payment triggers
- **Frontend**: 
  - Milestone creation and scheduling
  - Gate approval workflow
  - Gantt chart visualization
  - Milestone-based billing setup
- **Backend Models**:
  - `Milestone` - Project deliverable with due date
  - `MilestoneApproval` - Client sign-off on completion
  - `MilestonePaymentTrigger` - Billing trigger
- **Rules**:
  - Can't bill until milestone approved
  - Auto-generates invoice line items
  - Historical completion tracking
  - Variance analysis (planned vs actual)

#### P2.4 Expense Tracking Form
- **Purpose**: Out-of-pocket expenses allocated to projects
- **Frontend**: 
  - Expense entry form (category, amount, receipt)
  - Expense approval workflow
  - Expense reimbursement dashboard
  - Expense allocation to projects
- **Backend Models**:
  - `Expense` - Expense entry with category and receipt
  - `ExpenseCategory` - Travel, equipment, supplies, etc.
  - `ExpenseApproval` - Manager approval
  - `ExpenseAllocation` - Links expense to project
- **Rules**:
  - Receipt upload required
  - Amount limits per category (configurable)
  - Approval required > $500 (configurable)
  - Invoice inclusion automatic

### Priority 3: Project Governance (Operational Excellence)

#### P3.1 Status Report Form
- **Purpose**: Regular project health communication
- **Frontend**: 
  - Status report template form
  - Dashboard for report history
  - Client/stakeholder report sending
  - Health indicator (red/yellow/green)
- **Backend Models**:
  - `StatusReport` - Report instance
  - `StatusReportItem` - Accomplishments, risks, upcoming
  - `StatusReportRecipient` - Who receives reports
- **Rules**:
  - Scheduled reports (weekly, bi-weekly, monthly)
  - Auto-generation with basic metrics
  - Email delivery to stakeholders
  - Archive for compliance

#### P3.2 Risk Register & Issues Log
- **Purpose**: Track and manage project risks
- **Frontend**: 
  - Risk entry form (description, probability, impact)
  - Issue creation from risks
  - Mitigation tracking
  - Risk dashboard with heat map
  - Issue resolution workflow
- **Backend Models**:
  - `Risk` - Risk identification and scoring
  - `RiskMitigation` - Mitigation strategy
  - `Issue` - Escalated risk as issue
  - `IssueResolution` - Resolution tracking
- **Rules**:
  - Risk score = probability × impact
  - Auto-escalation rules
  - Mitigation due date tracking
  - Historical trending

#### P3.3 Meeting Notes & Action Items
- **Purpose**: Document decisions and accountability
- **Frontend**: 
  - Meeting notes form
  - Action item assignment
  - Action item tracking dashboard
  - Decision log
- **Backend Models**:
  - `MeetingNote` - Meeting documentation
  - `ActionItem` - Task with owner and due date
  - `Decision` - Recorded decisions
- **Rules**:
  - Action items auto-link to project
  - Owner notifications for due dates
  - Historical notes for audit trail

### Priority 4: Custom Software Development Forms

#### P4.1 Technical Requirements Specification (TRS)
- **Purpose**: Document technical needs and design
- **Frontend**: 
  - TRS form with sections (requirements, constraints, architecture)
  - Document editor with versioning
  - Approval workflow
  - Traceability matrix
- **Backend Models**:
  - `TechRequirementSpec` - TRS document
  - `TRSVersion` - Version history
  - `TechRequirement` - Individual requirement
  - `TRSApproval` - Client/arch sign-off
- **Rules**:
  - Required before development SOW
  - Version control with change tracking
  - Traceability to test cases
  - Impact analysis on changes

#### P4.2 UAT Planning & Execution
- **Purpose**: User acceptance testing coordination
- **Frontend**: 
  - UAT test case entry
  - Test execution tracker
  - Pass/fail/defect recording
  - UAT sign-off form
- **Backend Models**:
  - `UATTestCase` - Test case definition
  - `UATExecution` - Test execution record
  - `UATDefect` - Defect found during UAT
  - `UATSignOff` - Client acceptance
- **Rules**:
  - Can't move to production without UAT sign-off
  - Defects created during UAT
  - UAT period time tracking
  - Pass rate reporting

#### P4.3 Code Review & Quality Checklist
- **Purpose**: Quality assurance tracking
- **Frontend**: 
  - Code review checklist form
  - Review assignment
  - Review status dashboard
  - Quality metrics reporting
- **Backend Models**:
  - `CodeReview` - Review instance linked to deliverable
  - `ReviewChecklistItem` - Individual checks
  - `CodeDefect` - Issues found during review
- **Rules**:
  - Review required before merge/deploy
  - Checklist completion mandatory
  - Defects tracked for resolution
  - Historical metrics

#### P4.4 Release & Deployment Checklist
- **Purpose**: Safe production deployment
- **Frontend**: 
  - Pre-deployment checklist form
  - Deployment execution tracking
  - Rollback procedure documentation
  - Post-deployment verification
- **Backend Models**:
  - `Deployment` - Deployment instance
  - `DeploymentChecklist` - Pre-deployment items
  - `DeploymentLog` - Execution log
  - `PostDeploymentCheck` - Verification steps
- **Rules**:
  - All checklist items must be completed
  - Signed off by technical lead + PM
  - Rollback procedure documented
  - Deployment window respected

#### P4.5 Defect/Bug Tracking
- **Purpose**: Track and resolve issues in development
- **Frontend**: 
  - Bug entry form (description, severity, reproducibility)
  - Bug status workflow (new → assigned → fixed → verified → closed)
  - Bug dashboard with filtering
  - Triage queue
- **Backend Models**:
  - `Defect` - Bug/issue in deliverable
  - `DefectSeverity` - Critical, High, Medium, Low
  - `DefectResolution` - Fix and verification
  - `DefectReopen` - Reopened if fix didn't work
- **Rules**:
  - Critical/High must be addressed before release
  - Can't close without verification
  - Reopening tracked for quality metrics
  - Closure reason documented

#### P4.6 Knowledge Transfer & Handoff
- **Purpose**: Document system knowledge for client
- **Frontend**: 
  - Knowledge transfer documentation form
  - Training session tracking
  - Document repository
  - Support contact information
- **Backend Models**:
  - `KnowledgeTransferSession` - Training session
  - `KnowledgeDocument` - Training materials
  - `TrainingAttendee` - Who attended
  - `SupportHandoff` - Post-implementation support plan
- **Rules**:
  - Required before project close
  - Attendance tracked
  - Documents versioned
  - Completion sign-off by client

### Priority 5: Compliance & Legal Forms

#### P5.1 Data Security & Privacy Agreement
- **Purpose**: Protect sensitive data handling
- **Frontend**: 
  - DPA template selection/customization
  - Data classification form
  - Security requirement checklist
  - Signature workflow
- **Backend Models**:
  - `DataPrivacyAgreement` - DPA with status
  - `DataClassification` - Data types handled
  - `SecurityRequirement` - Specific requirements
- **Rules**:
  - Required if handling customer data
  - Annual review mandatory
  - Compliance attestation linked

#### P5.2 IP Ownership Agreement
- **Purpose**: Clarify intellectual property rights
- **Frontend**: 
  - IP agreement template
  - Ownership model selection
  - License grant terms
  - Approval workflow
- **Backend Models**:
  - `IPAgreement` - Agreement instance
  - `IPCategory` - Code, documentation, methodologies
  - `OwnershipModel` - Client-owned, Joint, Company-retained
- **Rules**:
  - Signed before development begins
  - Auto-incorporated into SOW terms
  - Historical reference for disputes

#### P5.3 Compliance Attestation Tracking
- **Purpose**: Track compliance certifications
- **Frontend**: 
  - Compliance checklist (SOC 2, ISO 27001, HIPAA, GDPR, etc.)
  - Attestation document upload
  - Expiration tracking
  - Compliance dashboard
- **Backend Models**:
  - `ComplianceAttestation` - Certification instance
  - `ComplianceRequirement` - What client requires
  - `AttestationDocument` - Proof document
- **Rules**:
  - Auto-alert 30 days before expiration
  - Required fields block quote/SOW
  - Version history maintained

### Priority 6: Client Portal & Visibility

#### P6.1 Client Dashboard
- **Purpose**: Read-only visibility for clients
- **Frontend**: 
  - Project status summary
  - Invoice and payment tracking
  - Document access
  - Timesheet visibility (optional)
  - Milestone progress
- **Backend**: 
  - Client-specific view restrictions
  - Read-only endpoints
  - Activity feed
- **Rules**:
  - Clients see only their projects
  - No modification permissions
  - Audit trail of access

#### P6.2 Client Approval Workflows
- **Purpose**: Client sign-off on deliverables
- **Frontend**: 
  - Approval notification email
  - Web form for acceptance/rejection
  - Feedback capture
- **Backend Models**:
  - `ClientApprovalRequest` - What needs approval
  - `ClientApprovalResponse` - Client response
- **Rules**:
  - Non-repudiation (signed and timestamped)
  - Prevents progression until approved

---

## Phase-by-Phase Implementation Plan

This section details how to implement all missing forms and documents in a structured, phased approach that prioritizes business value and legal risk reduction.

### Phase Structure

Each phase includes:
- **Duration**: Estimated timeline
- **Business Value**: Revenue impact and risk reduction
- **Technical Complexity**: Dev effort estimate
- **Frontend Changes**: UI/forms required
- **Backend Changes**: Models, endpoints, services
- **Database Changes**: Schema additions
- **Testing Requirements**: Coverage targets
- **Integration Points**: Where it connects to existing code
- **Success Criteria**: How to measure completion

---

### PHASE 1: Client Onboarding & Legal Foundation (Weeks 1-4)

**Goal**: Establish legal framework and client relationship foundation  
**Business Impact**: Eliminates legal risk, enables formal client relationships  
**Technical Complexity**: Medium (new models, some complex workflows)

#### Phase 1 Overview

This phase establishes the legal and contractual foundation for all client engagements. Without this, the company is exposed to IP disputes, scope creep, and legal liability. All subsequent phases depend on completion of this phase.

#### 1.1 MSA Management System

**Business Context**: Professional services companies MUST have a Master Service Agreement that defines the terms of engagement. Without this, clients can claim IP ownership, dispute rates, or refuse to pay.

**Files to Create/Modify**:
- `app/models/msa.py` (NEW)
- `app/routers/msa.py` (NEW)
- `app/services/msa_service.py` (NEW)
- `app/database/models.py` (UPDATE - add MSA models)
- Database migration for MSA tables
- `tests/test_msa.py` (NEW)

**Pydantic Models to Implement**:
```python
# app/models/msa.py

class MSATemplateBase:
    """Base template for reusable MSA templates"""
    name: str  # e.g., "Standard Services MSA", "Retainer MSA"
    content: str  # Template text with placeholders
    version: str  # Template version
    terms_days: int  # Default payment terms
    renewal_period_days: int  # Auto-renewal period

class MSACreate:
    """Request to create new MSA with client"""
    client_id: int
    template_id: int
    customizations: str | None  # Any custom terms
    effective_date: date
    expiration_date: date

class MSAResponse:
    """Response with MSA details"""
    id: int
    client_id: int
    template_id: int
    status: str  # draft, signed, expired, renewed
    current_version: int
    effective_date: date
    expiration_date: date
    signed_date: date | None
    signed_by: str | None
    created_at: datetime
    updated_at: datetime

class MSASignatureRequest:
    """Request to sign MSA"""
    signer_name: str
    signer_email: str
    signer_title: str
    signature_date: date
```

**SQLAlchemy Models to Implement**:
```python
# In app/database/models.py

class MSATemplate(Base):
    """MSA template for reuse across clients"""
    __tablename__ = "msa_templates"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    content = Column(Text, nullable=False)  # Template with {{placeholders}}
    version = Column(String(20), nullable=False)
    default_terms_days = Column(Integer, default=30)
    default_renewal_days = Column(Integer, default=365)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    msas = relationship("MSA", back_populates="template")

class MSA(Base):
    """Master Service Agreement for a client"""
    __tablename__ = "msas"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("msa_templates.id"), nullable=False)
    status = Column(String(50), default="draft", nullable=False)  # draft, signed, expired, renewed
    current_version = Column(Integer, default=1)
    customizations = Column(Text, nullable=True)
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    renewal_date = Column(Date, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))
    
    client = relationship("Client", back_populates="msas")
    template = relationship("MSATemplate", back_populates="msas")
    signatures = relationship("MSASignature", back_populates="msa", cascade="all, delete-orphan")

class MSASignature(Base):
    """Signature record on MSA"""
    __tablename__ = "msa_signatures"
    id = Column(Integer, primary_key=True)
    msa_id = Column(Integer, ForeignKey("msas.id"), nullable=False)
    signer_name = Column(String(255), nullable=False)
    signer_email = Column(String(255), nullable=False)
    signer_title = Column(String(255), nullable=True)
    signature_date = Column(Date, nullable=False)
    signed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    msa = relationship("MSA", back_populates="signatures")
    signed_by_user = relationship("User")

class MSAVersion(Base):
    """Version history of MSA changes"""
    __tablename__ = "msa_versions"
    id = Column(Integer, primary_key=True)
    msa_id = Column(Integer, ForeignKey("msas.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    change_summary = Column(Text, nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    msa = relationship("MSA")
    changed_by_user = relationship("User")
```

**API Endpoints to Create** (`app/routers/msa.py`):
```
POST /api/v1/msas/templates - Create MSA template (Admin only)
GET /api/v1/msas/templates - List templates
GET /api/v1/msas/templates/{id} - Get template details

POST /api/v1/msas - Create MSA with client
GET /api/v1/msas - List MSAs (filtered by client, status)
GET /api/v1/msas/{id} - Get MSA details
PUT /api/v1/msas/{id} - Update MSA (before signing)
POST /api/v1/msas/{id}/sign - Record signature
POST /api/v1/msas/{id}/renew - Renew expired MSA
DELETE /api/v1/msas/{id} - Archive MSA (soft delete)

GET /api/v1/msas/{id}/versions - MSA version history
GET /api/v1/msas/client/{client_id} - Get client's current MSA
```

**Business Logic to Implement** (`app/services/msa_service.py`):
- MSA status transitions (draft → signed → active → expired → renewed)
- Auto-generate MSA from template with client data
- Validate expiration dates
- Auto-generate renewal notifications (30 days before expiration)
- Prevent SOW creation if MSA not signed (configurable)
- Prevent invoice generation if MSA expired (configurable)
- Version control on amendments
- Email notifications for signature required
- Audit logging on all changes

**Database Migration**:
```python
# alembic/versions/YYYYMMDD_hhmmss_add_msa_tables.py

def upgrade():
    op.create_table('msa_templates', ...)
    op.create_table('msas', ...)
    op.create_table('msa_signatures', ...)
    op.create_table('msa_versions', ...)

def downgrade():
    op.drop_table('msa_versions')
    op.drop_table('msa_signatures')
    op.drop_table('msas')
    op.drop_table('msa_templates')
```

**Testing Requirements**:
- Test MSA creation and template rendering
- Test signature workflow
- Test expiration detection and renewal
- Test MSA required for SOW creation
- Test MSA required for invoicing
- Test version history tracking
- Test RBAC (only admin/PM can sign)
- Test audit logging
- Target: 85% coverage for MSA module

**Frontend Implementation** (React/TypeScript):
```typescript
// Components to Create:
- MSATemplateForm - Create/edit templates
- MSACreationForm - Create MSA for client
- MSASignatureForm - Collect signatures
- MSAList - List MSAs with status
- MSADetail - View MSA with actions
- MSARenewalModal - Renew expired MSA
- MSAVersionHistory - View all versions
- MSAExpirationAlert - Show expiring MSAs

// Features:
- Template selection with preview
- Automatic client data population
- Signature workflow (multi-signer support)
- Email signature links for clients
- Version comparison
- PDF export
- Integration with Client model
```

---

#### 1.2 NDA Management

**Business Context**: NDAs protect both parties' confidential information. Without one, consultants could legally share client info, or clients could claim consultants stole IP.

**Files to Create/Modify**:
- `app/models/nda.py` (NEW)
- `app/routers/nda.py` (NEW)
- `app/services/nda_service.py` (NEW)
- `app/database/models.py` (UPDATE - add NDA model)
- Database migration for NDA tables
- `tests/test_nda.py` (NEW)

**Pydantic Models**:
```python
class NDATemplate(BaseModel):
    name: str
    content: str
    nda_type: str  # mutual, unidirectional_to_us, unidirectional_to_client
    duration_years: int

class NDACreate(BaseModel):
    client_id: int
    template_id: int
    effective_date: date
    expiration_date: date

class NDAResponse(BaseModel):
    id: int
    client_id: int
    template_id: int
    status: str  # draft, signed, active, expired
    effective_date: date
    expiration_date: date
    signed_date: date | None
    created_at: datetime
```

**SQLAlchemy Models**:
```python
class NDATemplate(Base):
    __tablename__ = "nda_templates"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    nda_type = Column(String(50), nullable=False)  # Type of NDA
    duration_years = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    ndas = relationship("NDA", back_populates="template")

class NDA(Base):
    __tablename__ = "ndas"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("nda_templates.id"), nullable=False)
    status = Column(String(50), default="draft")  # draft, signed, active, expired
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    signed_date = Column(Date, nullable=True)
    signed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    client = relationship("Client")
    template = relationship("NDATemplate")
    signatures = relationship("NDASignature", cascade="all, delete-orphan")

class NDASignature(Base):
    __tablename__ = "nda_signatures"
    id = Column(Integer, primary_key=True)
    nda_id = Column(Integer, ForeignKey("ndas.id"), nullable=False)
    signer_name = Column(String(255), nullable=False)
    signer_email = Column(String(255), nullable=False)
    signature_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    nda = relationship("NDA")
```

**API Endpoints**:
```
POST/GET /api/v1/ndas/templates - Manage templates
POST /api/v1/ndas - Create NDA
GET /api/v1/ndas - List NDAs
POST /api/v1/ndas/{id}/sign - Sign NDA
GET /api/v1/clients/{id}/nda - Get client's current NDA
```

**Business Logic**:
- NDA required before SOW creation (configurable)
- Auto-notification when NDA expires
- Can't start project work without signed NDA
- Track NDA violations (if implemented)
- Multi-signer support

**Testing**: 85% coverage - test creation, signing, expiration, blocking SOW

---

#### 1.3 Client Intake Form

**Business Context**: Professional consulting companies collect detailed client information upfront: company structure, contacts, certifications, compliance needs, communication preferences.

**Files to Create/Modify**:
- `app/models/client_intake.py` (NEW)
- `app/routers/client_intake.py` (NEW)
- `app/services/client_intake_service.py` (NEW)
- `app/database/models.py` (UPDATE - add ClientIntake model)
- Database migration
- `tests/test_client_intake.py` (NEW)

**Pydantic Models**:
```python
class ClientIntakeBase(BaseModel):
    # Company Information
    company_legal_name: str
    company_registration_number: str | None
    tax_id: str | None
    industry: str
    company_size: str  # 1-10, 11-50, 51-200, 200+
    
    # Primary Contact
    primary_contact_name: str
    primary_contact_email: EmailStr
    primary_contact_phone: str
    primary_contact_title: str
    
    # Billing Contact
    billing_contact_name: str
    billing_contact_email: EmailStr
    billing_contact_phone: str
    
    # Compliance & Legal
    compliance_requirements: list[str]  # SOC 2, ISO 27001, HIPAA, GDPR, etc.
    data_types_handled: list[str]  # PII, Financial, Health, IP, etc.
    security_level: str  # low, medium, high, critical
    is_public_sector: bool  # Government/public entities often need special handling
    
    # Communication Preferences
    preferred_communication: str  # email, phone, video call, in-person
    escalation_contact_name: str | None
    escalation_contact_email: str | None
    
    # Special Requirements
    special_requirements: str | None
    languages_required: list[str]

class ClientIntakeResponse(ClientIntakeBase):
    id: int
    client_id: int
    completed_by: int
    completed_at: datetime
    last_updated_at: datetime
```

**SQLAlchemy Models**:
```python
class ClientIntake(Base):
    __tablename__ = "client_intakes"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, unique=True)
    
    # Company Information
    company_legal_name = Column(String(255), nullable=False)
    company_registration_number = Column(String(100), nullable=True)
    tax_id = Column(String(50), nullable=True)
    industry = Column(String(100), nullable=False)
    company_size = Column(String(50), nullable=False)
    
    # Contacts
    primary_contact_name = Column(String(255), nullable=False)
    primary_contact_email = Column(String(255), nullable=False)
    primary_contact_phone = Column(String(50), nullable=False)
    primary_contact_title = Column(String(100), nullable=True)
    
    billing_contact_name = Column(String(255), nullable=False)
    billing_contact_email = Column(String(255), nullable=False)
    billing_contact_phone = Column(String(50), nullable=False)
    
    # Compliance
    compliance_requirements = Column(String(500), nullable=True)  # JSON array
    data_types_handled = Column(String(500), nullable=True)  # JSON array
    security_level = Column(String(50), nullable=False)
    is_public_sector = Column(Boolean, default=False)
    
    # Preferences
    preferred_communication = Column(String(100), nullable=False)
    escalation_contact_name = Column(String(255), nullable=True)
    escalation_contact_email = Column(String(255), nullable=True)
    special_requirements = Column(Text, nullable=True)
    languages_required = Column(String(500), nullable=True)  # JSON array
    
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))
    
    client = relationship("Client", back_populates="intake")
    documents = relationship("ClientIntakeDocument", cascade="all, delete-orphan")

class ClientIntakeDocument(Base):
    __tablename__ = "client_intake_documents"
    id = Column(Integer, primary_key=True)
    intake_id = Column(Integer, ForeignKey("client_intakes.id"), nullable=False)
    document_type = Column(String(100), nullable=False)  # Certification, Security Form, etc.
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    expiration_date = Column(Date, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    intake = relationship("ClientIntake")
    uploaded_by_user = relationship("User")
```

**API Endpoints**:
```
POST /api/v1/client-intakes - Create intake form
PUT /api/v1/client-intakes/{client_id} - Update intake
GET /api/v1/client-intakes/{client_id} - Get intake
POST /api/v1/client-intakes/{client_id}/documents - Upload document
GET /api/v1/client-intakes/{client_id}/documents - List documents
```

**Business Logic**:
- Intake required before first SOW (configurable)
- Auto-generate compliance checklist from requirements
- Document expiration tracking with alerts
- Audit trail of all updates
- Email confirmation when intake submitted
- Multi-step form validation

**Testing**: 85% coverage

---

### PHASE 2: Change Management & Scope Control (Weeks 5-8)

**Goal**: Implement change control to prevent scope creep and financial disputes  
**Business Impact**: Protects margin, provides audit trail for disputes  
**Technical Complexity**: Medium (complex approval workflows)

#### 2.1 Change Order Management

**Business Context**: Scope changes are the #1 source of project overruns and client disputes. Formal change orders ensure both parties agree to scope changes and associated cost/timeline adjustments.

[Implementation details follow same pattern as Phase 1...]

---

### PHASE 3: Resource Management & Capacity Planning (Weeks 9-12)

**Goal**: Track consultant allocation and prevent overbooking  
**Business Impact**: Improves utilization, prevents schedule conflicts  
**Technical Complexity**: Medium-High (capacity calculation algorithms)

---

### PHASE 4: Project Governance & Tracking (Weeks 13-16)

**Goal**: Implement status reporting, risk management, and milestone tracking  
**Business Impact**: Improves delivery quality, enables proactive management  
**Technical Complexity**: Medium (mostly form creation)

---

### PHASE 5: Custom Development Specific Forms (Weeks 17-20)

**Goal**: TRS, UAT, Code Review, Deployment tracking  
**Business Impact**: Ensures quality delivery for software projects  
**Technical Complexity**: High (complex validation logic)

---

### PHASE 6: Compliance & Legal Documentation (Weeks 21-24)

**Goal**: Track compliance certifications, agreements, privacy  
**Business Impact**: Legal protection, regulatory compliance  
**Technical Complexity**: Medium

---

### PHASE 7: Financial Enhancements (Weeks 25-28)

**Goal**: Expense tracking, profitability analysis, milestone billing  
**Business Impact**: Accurate project accounting and margin management  
**Technical Complexity**: High (complex financial calculations)

---

### PHASE 8: Client Portal & Visibility (Weeks 29-32)

**Goal**: Client-facing interface for transparency  
**Business Impact**: Improves client satisfaction and approval workflows  
**Technical Complexity**: High (frontend heavy)

---

## Summary by Implementation Level

### Quick Win (Can Start Immediately)
1. MSA Management - High value, moderate complexity
2. Change Order Form - Prevents scope creep
3. Client Intake - Builds relationship foundation

### Medium Priority (Start After Quick Wins)
4. Resource Allocation - Operational efficiency
5. Status Reports - Client communication
6. Project Milestones - Delivery tracking

### Higher Complexity (Start With Team)
7. Custom Development Forms - Domain-specific
8. Expense Tracking - Financial accuracy
9. Client Portal - Frontend heavy

---

## Key Principles for Implementation

1. **Incrementalism**: Each form can be implemented independently, but builds on core models
2. **Flexibility**: All rules (e.g., "MSA required") are configurable by organization
3. **Audit Trail**: Every form change is logged for compliance
4. **RBAC**: Each form respects role-based access control
5. **Client Approval**: Forms support client signatures where needed
6. **Integration**: Forms integrate with existing workflows (e.g., change orders affect SOW budget)
7. **Reporting**: Forms generate data for dashboard and reports
8. **Mobile-Ready**: Forms work on all devices
9. **Template System**: Forms use templates for consistency
10. **Version Control**: All changes are versioned for audit trail

---

## Technical Architecture for Forms

All forms follow this architecture:

```
Frontend Form Component
    ↓
Pydantic Request Model (validation)
    ↓
FastAPI Router Endpoint (authentication, RBAC)
    ↓
Service Layer (business logic, calculations)
    ↓
SQLAlchemy ORM Model (database)
    ↓
AuditLog (compliance)
    ↓
Email Notifications (workflows)
    ↓
Reports/Dashboards (visibility)
```

---

## Success Metrics

By end of Phase 8, Votra.io will have:

✅ Complete client onboarding workflow  
✅ Legal protection through MSA/NDA/IP agreements  
✅ Scope change management  
✅ Resource optimization  
✅ Project governance framework  
✅ Custom development quality assurance  
✅ Financial accuracy and profitability tracking  
✅ Client visibility and transparency  
✅ 80%+ test coverage  
✅ OWASP compliance  
✅ Audit trail for all transactions  

This positions Votra.io as an enterprise-grade consulting management platform that follows industry best practices and legal standards.

---

**Document Version**: 1.0  
**Last Updated**: February 3, 2026  
**Status**: Ready for Phase 1 Implementation
