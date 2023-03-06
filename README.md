# openalex-affiliation-country

***Exhibits cases where OpenAlex affiliation country detection could be improved***

In OpenAlex, an alignment pipeline is implemented to link raw harvested affiliations (particularly via web crawling I suppose) to standardised affiliations, described by a standard `display_name` and potentially an `id`, `ror` and `country_code`.

Therefore, it seems that the detection of affiliation countries is only done through the affiliation institutions, based on the raw_affiliation_string.
raw_affiliation_string ----> institutions ----> country

Nevertheless, the task of recognizing an institution in a raw affiliation string is probably more complex than the task of recognizing a country in a raw affiliation string.

We believe that many use cases using country affiliation can be developed from OpenAlex, but today the quality of this metadata still needs to be improved for the implementation of these use cases with OpenAlex to be fully relevant. For example, every country seeking to steer its public research policies needs to use a reliable basis for listing and analysing its scientific output.
A country, as well as international organisations, also want to be able to compare production from one country to another.
Or understanding the international mobility of researchers is also a matter of interest.

This repo lists a sample of cases where the country of affiliation present in OpenAlex appears potentially incorrect. We have used our own [affiliation-matching tool](https://github.com/dataesr/affiliation-matcher) to detect these cases, and this automatic tool itself is not perfect. Nevertheless, we believe that the vast majority of the cases raised here are of interest.

We present this data with the following fields

- **raw_affiliation_string**: raw affiliation string as present in OpenAlex

- **openalex_work_id**: work id in OpenAlex in which the raw_affiliation_string has been found

- **openalex_country**: country_code detected by OpenAlex for this raw_affiliation_string

- **openalex_display_name**: display name of the institution detected by OpenAlex

- **matched_country**: country_code matched by our affiliation-matching tool

  
We have separated the data into two files:

 -  **`missing_country_code.csv`**: cases where OpenAlex does not provide a country_code (but our affiliation-matching tool does)

e.g "*KU, Leuven, Leuven, Belgium*" from https://openalex.org/W3085273257 has no country_code in OpenAlex (should be 'BE')

 -  **`mismatch_country_code.csv`**: cases where OpenAlex **MAY** not provide an accurate country_code (at least our affiliation-matching tool find a different country_code). Again these detections were done automatically and **does** contain errors for sure, it is **NOT** a golden dataset, but again, we believe that the vast majority of the cases raised here are of interest.

e.g "*ANDRA, Ci2A, Soulaines-Dhuys, France*" from https://openalex.org/W2802150657 is matched by OpenAlex to "Australian National Drag Racing Association", country_code AU whereas it should be matched to country 'FR'.


# mailing list

https://groups.google.com/g/openalex-users/c/QKMM1rxjk9Y
