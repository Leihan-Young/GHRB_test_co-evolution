@Test
public void testGetConsumerKeyHashRanges() throws BrokerServiceException.ConsumerAssignException {
    ConsistentHashingStickyKeyConsumerSelector selector = new ConsistentHashingStickyKeyConsumerSelector(3);
    List<String> consumerName = Arrays.asList("consumer1", "consumer2", "consumer3");
    List<Consumer> consumers = new ArrayList<>();
    for (String s : consumerName) {
        Consumer consumer = mock(Consumer.class);
        when(consumer.consumerName()).thenReturn(s);
        selector.addConsumer(consumer);
        consumers.add(consumer);
    }
    Map<Consumer, List<Range>> expectedResult = new HashMap<>();
    expectedResult.put(consumers.get(0), Arrays.asList(
            Range.of(0, 330121749),
            Range.of(330121750, 618146114),
            Range.of(1797637922, 1976098885)));
    expectedResult.put(consumers.get(1), Arrays.asList(
            Range.of(938427576, 1094135919),
            Range.of(1138613629, 1342907082),
            Range.of(1342907083, 1797637921)));
    expectedResult.put(consumers.get(2), Arrays.asList(
            Range.of(618146115, 772640562),
            Range.of(772640563, 938427575),
            Range.of(1094135920, 1138613628)));
    for (Map.Entry<Consumer, List<Range>> entry : selector.getConsumerKeyHashRanges().entrySet()) {
        System.out.println(entry.getValue());
        Assert.assertEquals(entry.getValue(), expectedResult.get(entry.getKey()));
        expectedResult.remove(entry.getKey());
    }
    Assert.assertEquals(expectedResult.size(), 0);
}
