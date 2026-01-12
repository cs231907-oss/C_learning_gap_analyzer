#to send warining/hint
def issue(severity,message,lineno=None):
    if lineno:
        return f"[{severity}] Line {lineno}: {message}"
    return f"[{severity}] {message}"
#to avoid duplicate errors
def unique_preserve_order(items):
    seen=set()
    result=[]
    for issue in items:
        key = (issue.get("line"),issue.get("code"),issue.get("severity"))
        if key not in seen:
            seen.add(key)
            result.append(issue
                          )
    return result

# Issue codes/Category of errors
SCANF_NO_SEMICOLON = "SCANF_NO_SEMICOLON"
SCANF_NO_FORMAT = "SCANF_NO_FORMAT"
SCANF_PTR_REQUIRED = "SCANF_PTR_REQUIRED"
SCANF_INVALID_SPECIFIER = "SCANF_INVALID_SPECIFIER"

PRINTF_NO_SEMICOLON = "PRINTF_NO_SEMICOLON"
PRINTF_NO_FORMAT = "PRINTF_NO_FORMAT"
PRINTF_PTR_MISMATCH = "PRINTF_PTR_MISMATCH"
PRINTF_ARG_MISSING = "PRINTF_ARG_MISSING"


HEADER_MISSING_STDIO = "HEADER_MISSING_STDIO"
HEADER_UNUSED_CONIO = "HEADER_UNUSED_CONIO"
HEADER_UNUSED_STRING = "HEADER_UNUSED_STRING"


#to analyze scanf while getting lineno.
def analyze_scanf(code):
    issues = []

    for lineno, line in enumerate(code.splitlines(),start=1):
        if "scanf(" in line:
            if ";" not in line:
                issues.append({
                    "line":lineno,
                    "severity":"Error",
                    "code":SCANF_NO_SEMICOLON,
                    "details":{}
                })
            
            if '"' not in line:
                issues.append({
                    "line":lineno,
                    "severity":"Error",
                    "code":SCANF_NO_FORMAT,
                    "details":{}
                })
            
            format_specs=extract_format_scanf_specifiers(line)

            #%p should not be used in scanf
            if "%p" in format_specs:
                issues.append({
                    "line":lineno,
                    "severity":"Error",
                    "code":SCANF_INVALID_SPECIFIER,
                    "details":{}
                })
            #address operator required for numeric inputs
            requires_address= any(spec  in ["%d","%f","%c"] for spec in format_specs)

            if requires_address and "&" not in line:
                issues.append({
                    "line":lineno,
                    "severity":"Error",
                    "code":SCANF_PTR_REQUIRED,
                    "details":{}
                })
    return unique_preserve_order(issues)

#token extraction for scanf specifiers to avoid false positives
def extract_format_scanf_specifiers(line):
    specs=[]
    in_string = False
    buffer = ""

    for char in line:
        if char == '"':
            in_string = not in_string
            buffer=""
            continue

        if in_string:
            buffer += char
            if buffer.endswith(("%d","%f", "%c", "%s", "%p")):
                specs.append(buffer[-2:])

    return specs

#to analayze printf while getting lineno.
def analyze_printf(code):
    issues = []

    for lineno, line in enumerate(code.splitlines(), start=1):
        if "printf(" in line:
            if ";" not in line:
                issues.append({
                    "line":lineno,
                    "severity":"Error",
                    "code":PRINTF_NO_SEMICOLON,
                    "details":{}
                })

            if '"' not in line:
                issues.append({
                    "line":lineno,
                    "severity":"Error",
                    "code":PRINTF_NO_FORMAT,
                    "details":{}
                })

            if "%d" in line and "," not in line.split(")", 1)[0]:
                issues.append({
                    "line":lineno,
                    "severity":"Error",
                    "code":PRINTF_ARG_MISSING,
                    "details":{
                        "specifier": "%d"
                    }
                })

            format_specs=extract_fromat_printf_specifiers(line)

            if "&" in line:
                if "%p" not in format_specs:
                    issues.append({
                "line": lineno,
                "severity": "Error",
                "code": PRINTF_PTR_MISMATCH,
                "details": {
                    "used": "&",
                    "allowed_specifier": "%p"
                }
                })

    return unique_preserve_order(issues)

#token extraction for printf specifiers to avoid false positives
def extract_fromat_printf_specifiers(line):
    specs = []
    in_string = False
    buffer = ""

    for char in line:
        if char == '"':
            in_string=not in_string
            buffer=""
            continue

        if in_string:
            buffer += char
            if char=='d' and buffer.endswith('%d'):
                specs.append('%d')
            if char=='p' and buffer.endswith('%p'):
                specs.append('%p')
    return specs

#to analyze the code
def analyze_c_code(code):
    issues=[]

    #rule 1: check for stdio.h
    if "printf" in code or "scanf" in code:
        if "#include <stdio.h>" not in code:
            issues.append({
                "line":"1",
                "severity":"Error",
                "code":HEADER_MISSING_STDIO,
                "details":{}
                })

    #rule 2: unnecessary headers
    if "#include <conio.h>" in code:
        issues.append({
                "line":"1",
                "severity":"Warning",
                "code":HEADER_UNUSED_CONIO,
                "details":{}
        })

    string_functions = ["strcpy", "strlen", "strcmp", "strcat"]
    if "#include <string.h>" in code:
        if not any(func in code for func in string_functions):
            issues.append({
                "line":"1",
                "severity":"Warning",
                "code":HEADER_UNUSED_STRING,
                "details":{}
        })
    issues.extend(analyze_printf(code))
    issues.extend(analyze_scanf(code))
    return issues

#to generate specific feedbaack
def generate_student_feedback(issue):
    code = issue["code"]
    severity = issue["severity"]
    details = issue.get("details", {})

    if code == PRINTF_PTR_MISMATCH:
        return (
            f"{severity}: You used '&' inside printf without a pointer format specifier.\n"
            "%d expects a value, not a memory address.\n"
            "Fix: Remove '&' or use %p if you want to print an address."
        )

    if code == PRINTF_ARG_MISSING:
        return (
            f"{severity}: You used a format specifier but did not pass a value.\n"
            "Each format specifier like %d needs a corresponding argument.\n"
            "Fix: Add a variable after the comma."
        )

    if code == PRINTF_NO_FORMAT:
        return (
            f"{severity}: You called printf without a format string.\n"
            "printf needs a format string to know what to print.\n"
            "Fix: Add a format string like \"%d\"."
        )

    if code == PRINTF_NO_SEMICOLON:
        return (
            f"{severity}: Missing semicolon at the end of the printf statement.\n"
            "In C, every statement must end with a semicolon.\n"
            "Fix: Add ';' at the end of the line."
        )

    if code == SCANF_NO_FORMAT:
        return (
            f"{severity}: You called scanf without a format string.\n"
            "scanf needs a format string to know what type of input to read.\n"
            "Fix: Add a format string like \"%d\"."
        )

    if code == SCANF_PTR_REQUIRED:
        return (
            f"{severity}: scanf requires the address of a variable.\n"
            "Input values must be stored in memory locations.\n"
            "Fix: Use '&' before the variable name."
        )

    if code == SCANF_INVALID_SPECIFIER:
        return (
            f"{severity}: %p is not valid for scanf input.\n"
            "scanf cannot read memory addresses directly.\n"
            "Fix: Use %d, %f, %c, or %s instead as needed."
        )

    if code == SCANF_NO_SEMICOLON:
        return (
            f"{severity}: Missing semicolon at the end of the scanf statement.\n"
            "C statements must end with a semicolon.\n"
            "Fix: Add ';' at the end of the line."
        )

    if code == HEADER_MISSING_STDIO:
        return (
            f"{severity}: stdio.h is missing but input/output functions are used.\n"
            "printf and scanf are defined in stdio.h.\n"
            "Fix: Add '#include <stdio.h>' at the top."
        )

    if code == HEADER_UNUSED_CONIO:
        return (
            f"{severity}: conio.h is included but not used.\n"
            "This header is non-standard and unnecessary here.\n"
            "Fix: Remove '#include <conio.h>'."
        )

    if code == HEADER_UNUSED_STRING:
        return (
            f"{severity}: string.h is included but no string functions are used.\n"
            "Unused headers increase confusion.\n"
            "Fix: Remove '#include <string.h>' or use string functions."
        )

    return f"{severity}: Issue detected, but no explanation is available."

#to return feedback
def feedback_engine(issues):
    feedback = []
    for issue in issues:
        message = generate_student_feedback(issue)
        feedback.append(f"Line {issue['line']}: {message}")

    return feedback





#____Used For Development Purpose____
#used for validating analyzer logic
# The following test cases were used during development to
# validate analyzer rules and identify edge cases.
#___________________________________

# student_code=[
# """
#    #include <stdio.h>
#    #include <conio.h> 
#     int main() { 
#       int a;
#  printf("input two nums");
#       scanf("%p", a)
#       printf(a); 
#     }  
# ""","""
#    #include <conio.h> 
#    int main() { 
#       int a;
#       int b;
#       scanf("%d",&a);
#       scanf("%d",&b);
#       printf("%d%d",a,b);
#  return 0;
#    } 
# ""","""
#   #include <stdio.h> 
#    #include <string.h>
#       int main() { 
#       int a; 
#       int b;
#     scanf("%d", &a); 
#     scanf("%d", &b); 
#     printf("%d",&a);
#     printf("%d",b)
#  return 0
#     }
# ""","""
# #include <stdio.h>
#  int main() {
#  int a;
#  int b;
#  printf("write the numbers:");
#  scanf("%d", &a);
#  scanf("%d", &b);
#     printf("the numbers:");
#      printf("%d and %d", a,b);
#      return 0;
#  }
# """]

# for i,code in enumerate(student_code,1):
#     print(f"student{i}")
#     raw_issues = analyze_c_code(code)
#     student_feedback = feedback_engine(raw_issues)

#     for msg in student_feedback:
#         print(msg)
