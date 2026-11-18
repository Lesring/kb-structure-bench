/* CWE: 999 synthetic marker only. Not a Juliet file and not an exploit. */
void CWE999_Synthetic__01_bad(void) {
    /* POTENTIAL FLAW: marker */
    int *p = 0;
    (void)p;
}

static void goodG2B(void) {
    /* FIX: marker */
    int *p = 0;
    (void)p;
}

void CWE999_Synthetic__01_good(void) {
    goodG2B();
}

#ifdef INCLUDEMAIN
int main(void) {
    printLine("Calling good()...");
    CWE999_Synthetic__01_good();
    printLine("Calling bad()...");
    CWE999_Synthetic__01_bad();
    return 0;
}
#endif
