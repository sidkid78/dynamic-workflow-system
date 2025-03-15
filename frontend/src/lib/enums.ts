// lib/enums.ts
export enum MedicalSpecialty {
    CARDIOLOGY = "cardiology",
    NEUROLOGY = "neurology",
    ONCOLOGY = "oncology",
    PEDIATRICS = "pediatrics",
    EMERGENCY = "emergency",
    GENERAL = "general_practice",
    SURGERY = "surgery",
    RADIOLOGY = "radiology"
  }
  
  export enum ClinicalRole {
    PHYSICIAN = "physician",
    RESIDENT = "resident",
    MEDICAL_STUDENT = "medical_student",
    NURSE = "nurse",
    SPECIALIST = "specialist",
    SURGEON = "surgeon"
  }
  
  export enum WorkflowState {
    RECEIVE_QUERY = "receive_query",
    ANALYZE_CLINICAL_CONTEXT = "analyze_clinical_context",
    RETRIEVE_MEDICAL_KNOWLEDGE = "retrieve_medical_knowledge",
    PROCESS_WITH_AZURE = "process_with_azure",
    APPLY_CLINICAL_HEURISTICS = "apply_clinical_heuristics",
    HIPAA_COMPLIANCE_CHECK = "hipaa_compliance_check",
    GENERATE_MEDICAL_RESPONSE = "generate_medical_response",
    ERROR = "error"
  }