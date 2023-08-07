package it.uniroma3.bigdata.ariaplus.cityMS.utility;

import it.uniroma3.bigdata.ariaplus.cityMS.domain.City;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Collectors;


public class CsvFileReaderUtil {
    private static final String SEPARATOR = ";";
    private static final Pattern PATTERN = Pattern.compile(SEPARATOR);

    public static List<City> loadCsvContentToList(BufferedReader br) {
        try {
            List<City> citiesList = br.lines().skip(1).map(line -> {
                final String[] lineArray = PATTERN.split(line);
                return City
                        .builder()
                        .name(lineArray[0].replaceAll("\"", ""))
                        .asciiName(lineArray[1].replaceAll("\"", ""))
                        .latitude(Float.parseFloat(lineArray[2].replaceAll("\"", "")))
                        .longitude(Float.parseFloat(lineArray[3].replaceAll("\"", "")))
                        .country(lineArray[4].replaceAll("\"", ""))
                        .iso2(lineArray[5].replaceAll("\"", ""))
                        .iso3(lineArray[6].replaceAll("\"", ""))
                        .adminName(lineArray[7].replaceAll("\"", ""))
                        .capital(lineArray[8].replaceAll("\"", ""))
                        .population(!"".equals(lineArray[9]) ? Integer.parseInt(lineArray[9].replaceAll("\"", "")) : null)
                        .id(lineArray[10].replaceAll("\"", ""))
                        .build();
            }).collect(Collectors.toList());
            br.close();
            return citiesList;
        } catch (IOException e) {
            e.printStackTrace();
            throw new RuntimeException(e);
        }
    }

}
