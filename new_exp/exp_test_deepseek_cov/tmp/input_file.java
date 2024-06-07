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
    expectedResult.put(consumers.get(1), Arrays