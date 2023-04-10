from gtd.input.csv_reader import CsvReader
from gtd.input.image_reader import ImageReader
from gtd.input.input_fraction_reader import InputFractionReader
from gtd.input.input_full_reader import InputFullReader


class CsvFullReader(InputFullReader, CsvReader):
    pass


class ImageFullReader(InputFullReader, ImageReader):
    pass


class ImageFractionReader(InputFractionReader, ImageReader):
    pass
