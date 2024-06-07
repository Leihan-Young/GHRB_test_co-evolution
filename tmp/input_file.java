    /**
     * As of Java 9, '_' is a keyword, and may not be used as an identifier.
     */
    @Test
    public void toEnumVarNameShouldNotResultInSingleUnderscore() throws Exception {
        Assert.assertEquals(fakeJavaCodegen.toEnumVarName(" ", "String"), "SPACE");
    }
