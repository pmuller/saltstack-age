/tmp/test-public:
  file.managed:
    - contents_pillar: public

/tmp/test-private:
  file.managed:
    - contents_pillar: private
