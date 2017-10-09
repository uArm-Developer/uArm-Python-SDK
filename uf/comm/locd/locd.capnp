@0xb9a0af4761f38486;

struct LoCD {
  srcAddrType  @0 :UInt8;
  srcAddr      @1 :Data;
  srcMac       @2 :UInt8;

  dstAddrType  @3 :UInt8;
  dstAddr      @4 :Data;
  dstMac       @5 :UInt8;

  union {
    icmp :group {
      type     @6 :UInt8;
    }
    udp :group {
      srcPort  @7 :UInt16;
      dstPort  @8 :UInt16;
    }
  }
  # call .which() to determine the packet type

  data         @9 :Data;
}

