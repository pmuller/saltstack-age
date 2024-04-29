{% set prefix = salt.pillar.get('prefix') %}

{{ prefix }}/test-public:
  file.managed:
    - contents_pillar: public

{{ prefix }}/test-private:
  file.managed:
    - contents_pillar: private
