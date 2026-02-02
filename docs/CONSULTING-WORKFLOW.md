# Votra.io Consulting Workflow: Client to Invoicing

**Document ID**: CONSULTING-WORKFLOW-001  
**Version**: 1.0.0  
**Last Updated**: 2026-02-01  
**Owner**: Product Team  
**Status**: Reference Guide

---

## Executive Summary

This document outlines the complete consulting workflow supported by Votra.io, from initial client engagement through project completion and invoicing. The platform automates industry-standard processes for managing consulting engagements, tracking resources, validating billable work, and generating accurate invoices.

---

## Complete Consulting Workflow

### Phase 1: Client Engagement & SOW Creation

#### 1.1 Client Onboarding
- **Action**: New client profile created in Votra.io
- **Data Captured**:
  - Company name and legal entity
  - Primary point of contact
  - Billing address and payment terms
  - Engagement type (hourly, fixed-price, retainer)
  - Communication preferences
- **Stakeholders**: Account Manager, Client Relations
- **Output**: Client record created, ready for SOW creation

#### 1.2 Scoping & SOW Preparation
- **Action**: Project Manager works with client to define scope
- **Process**:
  - Identify deliverables and success criteria
  - Determine timeline and milestones
  - Estimate resource requirements
  - Propose billable rates (hourly, daily, fixed)
- **Stakeholders**: Client, Project Manager, Finance
- **Tools**: SOW drafting workspace in Votra.io

#### 1.3 SOW Creation & Submission
- **Action**: Create SOW in Votra.io with:
  - Project description and objectives
  - Scope of work (deliverables, exclusions)
  - Timeline (start date, milestones, end date)
  - Resource allocation (consultants/roles)
  - Billing terms (rates, payment schedule, payment terms)
  - Terms & conditions
- **Validation**:
  - All rates must be ≥ minimum billable rate
  - Rates must be positive and non-zero
  - Timeline must be logical (start before end)
  - All required fields must be populated
- **Stakeholders**: Project Manager, Finance Lead
- **Output**: SOW created in "Draft" status

#### 1.4 Internal Approval
- **Action**: Finance and Management review and approve SOW
- **Process**:
  - Review project profitability (rates vs. resource costs)
  - Verify compliance with company standards
  - Approve or request revisions
- **Approval Flow**:
  - Draft → Pending Approval (submitted)
  - Pending Approval → Approved (approved by PM/Finance)
  - Pending Approval → Rejected (returned with notes)
  - Rejected → Draft (returned for revision)
- **Stakeholders**: Finance Lead, Project Manager, Executive (if required)
- **Output**: SOW moved to "Approved" status

#### 1.5 Client Presentation & Sign-off
- **Action**: Present SOW to client, obtain written approval
- **Process**:
  - Review SOW with client decision-makers
  - Address questions and requests
  - Obtain client signature/approval
- **Integration**: Approved SOW marked as "Client-Approved" in Votra.io
- **Stakeholders**: Project Manager, Client
- **Output**: SOW ready for project creation and resource allocation

---

### Phase 2: Project Setup & Resource Allocation

#### 2.1 Project Creation from SOW
- **Action**: Create project from approved SOW
- **Mapping**:
  - Project name/ID links to SOW
  - Timeline copied from SOW
  - Billable rates inherited from SOW
  - Client information inherited from SOW
- **Status**: Project created in "Planning" status
- **Stakeholders**: Project Manager
- **Output**: Project record created, ready for resource allocation

#### 2.2 Resource Allocation
- **Action**: Assign consultants/staff to project
- **Assignment Details**:
  - Consultant name and role
  - Allocation percentage (100% full-time, 50% part-time, etc.)
  - Rate (inherited from SOW or specific to consultant)
  - Start and end dates
- **Validation**:
  - Consultant availability checked
  - Rate must match SOW or be documented
  - Assignment dates must fall within project dates
- **Stakeholders**: Project Manager, Resource Manager
- **Output**: Consultants assigned to project

#### 2.3 Project Kickoff
- **Action**: Project status moved to "Active"
- **Process**:
  - Consultants notified of assignments
  - Project details and deliverables reviewed
  - Team communication channels established
- **Integration**: Start tracking billable time
- **Stakeholders**: All project team members
- **Output**: Project ready for timesheet entry

---

### Phase 3: Time Tracking & Validation

#### 3.1 Daily Timesheet Entry
- **Action**: Consultants enter hours worked on projects
- **Entry Details**:
  - Date of work
  - Project assigned
  - Hours worked (decimal format: 0.5, 1.0, 7.5, 8.0)
  - Task/activity description
  - Billable/non-billable classification
- **Constraints**:
  - Date must fall within project active dates
  - Consultant must be allocated to project
  - Hours cannot exceed 8 hours per day (configurable)
- **Stakeholders**: Consultants
- **Output**: Time entry recorded in "Draft" status

#### 3.2 Timesheet Validation
- **Action**: System and PM validate timesheet entries
- **Validation Rules**:
  - All hours fall within project date range
  - Consultant is allocated to project
  - No double-billing (same date/project, different entry)
  - Billable hours total doesn't exceed allocation
  - Reasonable hour entries (no 24-hour days)
- **Alerts**:
  - Entries outside project dates flagged
  - Entries by unallocated consultants flagged
  - Duplicate entries detected and merged
- **Stakeholders**: Project Manager, Finance
- **Output**: Timesheet validated and approved for billing

#### 3.3 Timesheet Approval
- **Action**: Project Manager approves timesheet
- **Process**:
  - Review all entries for accuracy
  - Verify against project scope
  - Approve or request revisions
- **Approval Flow**:
  - Draft → Pending Approval
  - Pending Approval → Approved (locked for invoice generation)
  - Pending Approval → Rejected (returned for correction)
- **Stakeholders**: Project Manager, Consultant (if revisions needed)
- **Output**: Approved timesheet ready for invoice generation

---

### Phase 4: Invoice Generation & Payment Processing

#### 4.1 Invoice Generation
- **Action**: System generates invoice from approved timesheets
- **Process**:
  - Collect all approved timesheets for billing period (weekly, bi-weekly, monthly)
  - Group by client and project
  - Calculate totals:
    - Hours × Rate = Line item total
    - Sum all line items = Invoice subtotal
    - Apply taxes/discounts if applicable = Invoice total
  - Create invoice with unique number and date
- **Invoice Details**:
  - Invoice number (sequential)
  - Invoice date
  - Due date (based on payment terms)
  - Client name and billing address
  - Project reference
  - Line items (consultant name, hours, rate, amount)
  - Subtotal, taxes, total
  - Payment instructions
  - Terms & conditions
- **Stakeholders**: Finance/Accountant
- **Output**: Invoice created in "Draft" status

#### 4.2 Invoice Review & QA
- **Action**: Finance reviews invoice before sending
- **Checks**:
  - Math verification (hours × rate calculations correct)
  - Client billing address correct
  - Rates match SOW
  - All timesheet entries included
  - No duplicate line items
  - Tax calculations correct
- **Corrections**:
  - Review flagged issues
  - Make corrections if needed
  - Re-validate totals
- **Stakeholders**: Accountant, Finance Lead
- **Output**: Invoice approved, moved to "Ready to Send" status

#### 4.3 Invoice Sending
- **Action**: Invoice sent to client
- **Process**:
  - Generate PDF of invoice
  - Send via email to billing contact
  - Log send date and method
  - Create delivery confirmation
- **Payment Information**:
  - Payment methods accepted
  - Wire transfer instructions (if applicable)
  - Credit card payment link (if available)
  - Payment terms (Net 30, Net 45, etc.)
- **Stakeholders**: Finance, Account Manager
- **Output**: Invoice status changed to "Sent"

#### 4.4 Payment Tracking
- **Action**: Track invoice payment status
- **Status Flow**:
  - Sent → Pending Payment
  - Pending Payment → Paid (upon receipt)
  - Pending Payment → Overdue (if not paid by due date)
  - Overdue → Paid (late payment received)
  - Sent → Partially Paid (partial payment received)
- **Data Tracked**:
  - Payment date
  - Payment method
  - Amount received
  - Reference number/check number
- **Reminders**:
  - Automated reminders 3 days before due date
  - Automated reminders 3 days after due date if not paid
- **Stakeholders**: Finance, Collections Team
- **Output**: Payment recorded, invoice marked as Paid

---

### Phase 5: Project Closure & Financial Close

#### 5.1 Project Completion
- **Action**: All deliverables completed and accepted by client
- **Process**:
  - Final deliverables submitted
  - Client sign-off obtained
  - Final timesheet entries made
  - All invoices sent
- **Status Change**: Project moved from "Active" to "Completed"
- **Stakeholders**: Project Manager, Client, Consultants
- **Output**: Project completion recorded

#### 5.2 Financial Close
- **Action**: Final reconciliation and financial reporting
- **Processes**:
  - Verify all billable hours captured
  - Verify all invoices sent and payment received
  - Calculate project profitability:
    - Total billable revenue
    - Less: Consultant costs (hours × cost rate)
    - Less: Overhead allocation
    - Equals: Project profit
  - Generate project final report
- **Stakeholders**: Finance, Project Manager, Accounting
- **Output**: Project financial close completed

#### 5.3 Project Reporting
- **Action**: Generate final project reports
- **Reports Generated**:
  - Project profitability report
  - Consultant hours and utilization
  - Budget vs. actual analysis
  - Client satisfaction review
- **Stakeholders**: Executive, Finance, Project Manager
- **Output**: Reports available for analysis and planning

---

## Key Validations & Business Rules

### Financial Accuracy
- ✅ **No negative rates**: All rates must be ≥ $0.00
- ✅ **Rate consistency**: Timesheet rates must match SOW
- ✅ **Calculation accuracy**: Hours × Rates = Line item totals
- ✅ **No double billing**: Prevent duplicate entries for same date/project

### Compliance & Audit Trail
- ✅ **Complete audit logging**: Track who made changes, when
- ✅ **State transitions logged**: Document SOW approval, invoice generation
- ✅ **Change history preserved**: Keep record of all edits
- ✅ **Financial compliance**: Ensure records suitable for audit

### Role-Based Access Control
- ✅ **Admin**: Full system access
- ✅ **Project Manager**: SOW approval, project setup, timesheet approval
- ✅ **Consultant**: Time entry only
- ✅ **Client**: View-only access to SOW, project status, invoices
- ✅ **Accountant**: Invoice generation, payment processing, reporting

### Data Integrity
- ✅ **Referential integrity**: Projects reference SOWs, timesheets reference projects, invoices reference timesheets
- ✅ **Orphan prevention**: Cannot delete client with active projects
- ✅ **State validation**: Cannot invoice unapproved timesheets
- ✅ **Amount reconciliation**: Invoice totals match timesheet amounts

---

## Industry-Standard Payment Terms

### Common Terms Supported
- **Net 15**: Payment due 15 days from invoice date
- **Net 30**: Payment due 30 days from invoice date (most common)
- **Net 45**: Payment due 45 days from invoice date
- **Net 60**: Payment due 60 days from invoice date
- **Due upon receipt**: Payment due immediately
- **Partial terms**: Deposit upon SOW approval, balance upon completion

---

## Consulting Metrics & KPIs

### Project Metrics
- **Billable Utilization**: % of time spent on billable vs. non-billable work
- **Project Profitability**: Revenue minus consultant costs and overhead
- **On-time Delivery**: % of projects completed by planned end date
- **Budget Adherence**: Actual hours vs. estimated hours

### Financial Metrics
- **Average Bill Rate**: Average hourly rate across all projects
- **Days Sales Outstanding (DSO)**: Average days to collect payment
- **Gross Margin**: Billable revenue vs. total consultant costs
- **Revenue per Consultant**: Total billable revenue divided by consultants

### Resource Metrics
- **Consultant Utilization**: % time spent on billable work
- **Resource Allocation**: Number of concurrent projects per consultant
- **Skills Utilization**: How often specialized skills are utilized
- **Bench Time**: Non-billable time between projects

---

## Integration Points

### With External Systems
- **Accounting Software**: Export invoices to QuickBooks, Xero, etc.
- **Payroll Systems**: Import consultant cost rates
- **Calendar/Scheduling**: Import project dates and consultant availability
- **Email/Communication**: Send SOW and invoice notifications

### Data Exports
- **Excel Reports**: Project profitability, consultant utilization
- **PDF Invoices**: For client distribution and archival
- **API Access**: For custom integrations and dashboards

---

## Error Handling & Dispute Resolution

### Common Issues
| Issue | Cause | Resolution |
|-------|-------|-----------|
| Invoice math error | System calculation bug | Regenerate invoice from timesheets |
| Missing timesheet hours | Consultant forgot to enter time | Edit timesheet and regenerate invoice |
| Wrong billing rate | Rate in timesheet doesn't match SOW | Correct rate in SOW and timesheets |
| Double billing detected | Duplicate timesheet entries | Merge duplicate entries, regenerate invoice |
| Invoice sent to wrong client | Client selection error | Recreate invoice with correct client |

### Dispute Process
1. Client disputes charge
2. Finance investigates (review SOW, timesheet, invoice)
3. Determine if error (ours) or misunderstanding (scope)
4. If error: Credit memo issued
5. If scope issue: Clarify with client and adjust future terms

---

## Conclusion

Votra.io automates the complete consulting workflow, from client engagement through invoicing, with built-in validations to ensure accurate billing, prevent double-billing, and maintain audit trails for compliance. The platform enables consulting firms to reduce administrative overhead while improving accuracy and project profitability visibility.
