/**
 * Validate URL format
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate Azure endpoint URL
 */
export function isValidAzureEndpoint(url: string): boolean {
  if (!isValidUrl(url)) return false;
  return url.includes('azure.com') || url.includes('cognitiveservices.azure.com') || url.includes('openai.azure.com');
}

/**
 * Validate file type
 */
export function isValidFileType(file: File, allowedTypes: string[]): boolean {
  return allowedTypes.includes(file.type) || allowedTypes.some(type => file.name.toLowerCase().endsWith(type));
}

/**
 * Validate file size (in bytes)
 */
export function isValidFileSize(file: File, maxSizeBytes: number): boolean {
  return file.size <= maxSizeBytes;
}

/**
 * Validate query text (not empty, within length limits)
 */
export function isValidQuery(query: string, minLength = 1, maxLength = 1000): boolean {
  const trimmed = query.trim();
  return trimmed.length >= minLength && trimmed.length <= maxLength;
}

/**
 * Validate number is within range
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max;
}

/**
 * Validate API key format (basic check for non-empty and length)
 */
export function isValidApiKey(key: string): boolean {
  return key.trim().length >= 10;
}

/**
 * Validate settings object has required fields
 */
export function validateSettings(settings: Record<string, any>): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!settings.azure_openai_endpoint || !isValidAzureEndpoint(settings.azure_openai_endpoint)) {
    errors.push('Invalid Azure OpenAI endpoint');
  }

  if (!settings.azure_openai_key || !isValidApiKey(settings.azure_openai_key)) {
    errors.push('Invalid Azure OpenAI API key');
  }

  if (!settings.azure_doc_intelligence_endpoint || !isValidAzureEndpoint(settings.azure_doc_intelligence_endpoint)) {
    errors.push('Invalid Azure Document Intelligence endpoint');
  }

  if (!settings.azure_doc_intelligence_key || !isValidApiKey(settings.azure_doc_intelligence_key)) {
    errors.push('Invalid Azure Document Intelligence API key');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Sanitize text input
 */
export function sanitizeInput(input: string): string {
  return input.trim().replace(/[<>]/g, '');
}
