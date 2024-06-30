// Fail to generate test fix. This is original test code.
@Test
void read() {
    List<String> resourceNameList = ClasspathResourceDirectoryReader.read("yaml").collect(Collectors.toList());
    assertThat(resourceNameList.size(), is(4));
    final String separator = File.separator;
    assertThat(resourceNameList, hasItems("yaml" + separator + "accepted-class.yaml", "yaml" + separator + "customized-obj.yaml", "yaml" + separator + "empty-config.yaml",
            "yaml" + separator + "shortcuts-fixture.yaml"));
}
