{% set prefix = salt.pillar.get('test:prefix') %}

{{ prefix }}/test-public:
  file.managed:
    - contents_pillar: test:public

{{ prefix }}/test-private:
  file.managed:
    - contents_pillar: test:private
